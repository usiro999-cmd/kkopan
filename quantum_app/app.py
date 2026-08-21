import json
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

try:
    from .drug_discovery import rank_candidates, rank_twin_profiles
    from .simulator import sample_measurements, simulate
except ImportError:
    from drug_discovery import rank_candidates, rank_twin_profiles
    from simulator import sample_measurements, simulate


APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"


def simulation_payload(data: object) -> dict[str, object]:
    if not isinstance(data, dict):
        raise ValueError("request body must be a JSON object")

    num_qubits = data.get("num_qubits", 3)
    gates = data.get("gates", [])
    shots = data.get("shots", 1024)
    if isinstance(shots, bool) or not isinstance(shots, int):
        raise ValueError("shots must be an integer")

    result = simulate(num_qubits, gates)
    states = []
    for index, (amplitude, probability) in enumerate(
        zip(result.amplitudes, result.probabilities)
    ):
        states.append(
            {
                "state": format(index, f"0{num_qubits}b"),
                "real": round(amplitude.real, 10),
                "imaginary": round(amplitude.imag, 10),
                "probability": round(probability, 10),
            }
        )

    return {
        "states": states,
        "counts": sample_measurements(result.probabilities, num_qubits, shots),
    }


def twin_simulation_payload(data: object) -> dict[str, object]:
    if not isinstance(data, dict):
        raise ValueError("request body must be a JSON object")
    left = data.get("left")
    right = data.get("right")
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise ValueError("left and right circuits must be JSON objects")
    if left.get("num_qubits", 3) != right.get("num_qubits", 3):
        raise ValueError("twin circuits must use the same number of qubits")

    with ThreadPoolExecutor(max_workers=2, thread_name_prefix="quantum-twin") as pool:
        left_future = pool.submit(simulation_payload, left)
        right_future = pool.submit(simulation_payload, right)
        left_result = left_future.result()
        right_result = right_future.result()

    left_probabilities = [state["probability"] for state in left_result["states"]]
    right_probabilities = [state["probability"] for state in right_result["states"]]
    distance = sum(
        abs(left_value - right_value)
        for left_value, right_value in zip(left_probabilities, right_probabilities)
    ) / 2
    overlap = sum(
        (left_value * right_value) ** 0.5
        for left_value, right_value in zip(left_probabilities, right_probabilities)
    )

    return {
        "left": left_result,
        "right": right_result,
        "comparison": {
            "similarity": round(overlap**2, 10),
            "total_variation_distance": round(distance, 10),
        },
    }


class QuantumAppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def _send_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path not in {
            "/api/simulate",
            "/api/twin",
            "/api/drug-ranking",
            "/api/drug-twin-ranking",
        }:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 1_000_000:
                raise ValueError("request body size is invalid")
            data = json.loads(self.rfile.read(content_length))
            if path == "/api/twin":
                payload = twin_simulation_payload(data)
            elif path == "/api/drug-twin-ranking":
                payload = rank_twin_profiles(data)
            elif path == "/api/drug-ranking":
                payload = rank_candidates(data)
            else:
                payload = simulation_payload(data)
            self._send_json(HTTPStatus.OK, payload)
        except (ValueError, json.JSONDecodeError) as error:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})


def create_server(
    host: str = "127.0.0.1", port: int = 0
) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), QuantumAppHandler)


def main() -> None:
    host, port = "127.0.0.1", 8000
    server = create_server(host, port)
    print(f"Quantum Circuit Lab: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
