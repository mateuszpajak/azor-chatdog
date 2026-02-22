from .base_tool import BaseTool

class AskForClarificationTool(BaseTool):
    """Asks the user to clarify by choosing one of 4 options."""

    @property
    def name(self) -> str:
        return "askForClarification"

    @property
    def description(self) -> str:
        return (
            """
            Użyj gdy pytanie użytkownika jest niejednoznaczne lub brakuje informacji. Jezeli nie potrafisz odpowiedziec na pytanie, uzyj tego narzedzia.
            Podaj pytanie doprecyzowujące oraz cztery opcje odpowiedzi. Użytkownik wybierze jedną z opcji (1-4), a wynik zostanie zwrócony do modelu.
            """
        )

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Pytanie doprecyzowujące do użytkownika",
                },
                "option1": {"type": "string", "description": "Opcja 1"},
                "option2": {"type": "string", "description": "Opcja 2"},
                "option3": {"type": "string", "description": "Opcja 3"},
                "option4": {"type": "string", "description": "Opcja 4"},
            },
            "required": ["question", "option1", "option2", "option3", "option4"],
        }

    def get_response_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "result": {
                    "type": "string",
                    "description": "Odpowiedź użytkownika w formacie: Użytkownik wybrał: [treść opcji]",
                },
            },
        }

    def execute(self, args: dict) -> str:
        from cli import console
        from cli.prompt import get_user_input

        question = args.get("question", "")
        options = [
            args.get("option1", ""),
            args.get("option2", ""),
            args.get("option3", ""),
            args.get("option4", ""),
        ]

        console.print_info("\n--- Doprecyzowanie ---")
        console.print_info(question)
        for i, opt in enumerate(options, 1):
            console.print_info(f"  {i}. {opt}")
        console.print_info("")

        while True:
            choice_input = get_user_input("Wybierz opcję (1-4): ").strip()
            if choice_input in ("1", "2", "3", "4"):
                idx = int(choice_input) - 1
                selected = options[idx]
                return f"Użytkownik wybrał: {selected}"
            console.print_error("Proszę wpisać liczbę od 1 do 4.")
