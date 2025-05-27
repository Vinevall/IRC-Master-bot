
class Log:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

    def info(self, message: str) -> None:
        print(f"{self.GREEN}[INFO] {message}{self.RESET}")

    def warn(self, message: str) -> None:
        print(f"{self.YELLOW}[WARN] {message}{self.RESET}")

    def error(self, message: str) -> None:
        print(f"{self.RED}[ERROR] {message}{self.RESET}")

