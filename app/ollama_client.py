"""
Resilient Ollama client:
- Longer HTTP timeout (300s) to tolerate initial model load on small VMs
- keep_alive to keep model in memory between requests
- Optional options: num_ctx to reduce memory; use_mmap=false if loads stall
Docs: /api/generate supports keep_alive and num_ctx in options. [2](https://docs.ollama.com/api/generate)[3](https://ollama.apidog.io/overview-875553m0)
Disabling mmap improved load speed for some setups (GitHub issue). [1](https://github.com/ollama/ollama/issues/4350)
"""

import httpx
from app.settings import settings


class OllamaClient:
    def __init__(self, host: str = settings.OLLAMA_HOST):
        self.host = host.rstrip("/")

    async def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.2,
        stop: list[str] | None = None,
        keep_alive: str = "30m",        # keep model resident for 30 minutes
        num_ctx: int = 2048,            # modest context to reduce memory footprint
        use_mmap: bool | None = None    # set to False if loads stall on your VM
    ) -> str:
        url = f"{self.host}/api/generate"

        options = {"temperature": temperature, "num_ctx": num_ctx}
        if use_mmap is not None:
            options["use_mmap"] = use_mmap

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,            # single consolidated response
            "keep_alive": keep_alive,   # documented in Ollama API
            "options": options
        }
        if stop:
            payload["stop"] = stop

        # Increase timeout to tolerate first load / CPU-only VM
        async with httpx.AsyncClient(timeout=600) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            return data.get("response", "")
