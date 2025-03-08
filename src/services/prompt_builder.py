import tiktoken

class PromptBuilder:
    def __init__(self):
        """
        Initializes the PromptBuilder with a GPT-4 tokenizer for counting tokens in messages.
        """
        self.tokenizer = tiktoken.get_encoding("gpt-4")

    def count_tokens(self, messages: list[dict[str, str]]) -> int:
        """
          Counts the total number of tokens in the list of messages.

          Args:
              messages (list[dict[str, str]]): A list of dictionaries where each dictionary contains
                                                a "role" (user or system) and the "content" (message text).

          Returns:
              int: The total number of tokens in the provided messages.
          """
        tokens = 0
        for message in messages:
            tokens += len(self.tokenizer.encode(message["content"]))
        return tokens

    def build_prompt(self, chat_history: list[dict[str, str]], user_input: str, rag_info: str, max_tokens=4000) -> list[dict[str, str]]:
        """
        Builds a prompt for the model by appending the user input and additional information to the chat history.
        The prompt is then adjusted to ensure it does not exceed the maximum token limit by removing older messages.

        Args:
            chat_history (list[dict[str, str]]): The current chat history (list of messages).
            user_input (str): The new input message from the user.
            rag_info (str): Additional information related to the retrieval-augmented generation (RAG).
            max_tokens (int): The maximum allowed token count for the prompt (default is 4000).

        Returns:
            list[dict[str, str]]: The adjusted chat history with the new prompt, within the token limit.
        """
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "system", "content": f"Additional info: {rag_info}"})

        total_tokens = self.count_tokens(chat_history)

        while total_tokens > max_tokens:
            chat_history.pop(0)
            total_tokens = self.count_tokens(chat_history)

        return chat_history