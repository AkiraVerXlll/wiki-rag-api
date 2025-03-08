import tiktoken

class PromptBuilder:
    """
    A class responsible for building and managing prompts for the language model.
    """

    def __init__(self, encoding="gpt-4"):
        """
        Initialize the PromptBuilder with a GPT-4 tokenizer for counting tokens in messages.

        :param encoding: str, optional
            The encoding to use for tokenization (default is "gpt-4").
        """
        self.tokenizer = tiktoken.get_encoding(encoding)

    def count_tokens(self, messages: list[dict[str, str]]) -> int:
        """
        Count the total number of tokens in a list of messages.

        :param messages: list[dict[str, str]]
            A list of dictionaries where each dictionary contains a "role" (user or system)
            and the "content" (message text).

        :return: int
            The total number of tokens in the provided messages.
        """
        tokens = 0
        for message in messages:
            tokens += len(self.tokenizer.encode(message["content"]))
        return tokens

    def build_prompt(self, chat_history: list[dict[str, str]], user_input: str, rag_info: str, max_tokens=4000) -> list[dict[str, str]]:
        """
        Build a prompt for the model by appending the user input and additional information to the chat history.
        Adjust the prompt to ensure it does not exceed the maximum token limit by removing older messages.

        :param chat_history: list[dict[str, str]]
            The current chat history (list of messages).
        :param user_input: str
            The new input message from the user.
        :param rag_info: str
            Additional information related to the retrieval-augmented generation (RAG).
        :param max_tokens: int, optional
            The maximum allowed token count for the prompt (default is 4000).

        :return: list[dict[str, str]]
            The adjusted chat history with the new prompt, within the token limit.
        """
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "system", "content": f"Additional info: {rag_info}"})

        total_tokens = self.count_tokens(chat_history)

        while total_tokens > max_tokens:
            chat_history.pop(0)
            total_tokens = self.count_tokens(chat_history)

        return chat_history