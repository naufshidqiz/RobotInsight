# RobotInsight test phrases

Say **“Hey In Site”** first, wait for the assistant’s greeting, then try one phrase at a time.

| Feature | Phrase to say | Expected behavior |
| --- | --- | --- |
| Wake word | “Hey In Site” | Robot wakes and invites you to speak. |
| Time | “What time is it?” | Gives the computer’s current local time. |
| Explicit web search | “Search for the latest NASA Artemis news.” | Shows the searching status, searches the web, and answers from the results. |
| Automatic knowledge search | “What is a transistor?” | Searches the web without needing the words “search for.” |
| Explanation search | “Explain why the sky looks blue.” | Searches for supporting information and summarizes it. |
| Current information | “Who is the current president of the United States?” | Searches for a current answer rather than relying on model memory. |
| Camera description | “What do you see?” | Captures an image and describes what the camera can see. |
| Camera capture | “Take a picture.” | Captures an image and analyzes it. |
| Appearance question | “How do I look?” | Uses the camera to answer. |
| General conversation | “Tell me a short joke.” | Replies using the local language model without web search. |
| Spoken punctuation cleanup | “Say this sentence: Hello, world! I’m ready.” | Speaks the words without reading punctuation marks aloud. |
| Follow-up conversation | After an answer, say “Explain more,” “Why?” or “Can you explain that more simply?” | Uses the previous answer as context and gives a short follow-up without starting a new web search. |
| Return to standby | After the greeting, stay silent until the silence timeout. | Gives the standby message and returns to waiting for the wake word. |

The web, language-model, microphone, and camera phrases require their matching service or device to be available. In particular, web-search answers also need Ollama running in the current configuration.
