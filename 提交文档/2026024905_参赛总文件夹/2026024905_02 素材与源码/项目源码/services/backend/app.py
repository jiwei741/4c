from __future__ import annotations

import sys
from pathlib import Path


SERVICE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = SERVICE_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spatio_eco_backend.api_fastapi import FASTAPI_AVAILABLE, create_app


app = create_app() if FASTAPI_AVAILABLE else None


def main() -> None:
    if app is None:
        from spatio_eco_backend.api_stdlib import run

        run()
        return

    try:
        import uvicorn
    except ImportError:
        from spatio_eco_backend.api_stdlib import run

        run()
        return

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
