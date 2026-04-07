#!/usr/bin/env python3

from src.chatbot.chatbot import ask_chatbot
from src.chatbot.tools import is_safe
from src.chatbot.tts import speak
from src.chatbot.stt import record_and_transcribe
from src.chatbot.image_gen import generate_book_image


def main() -> None:
    print("Smart Librarian started.")
    print("Type 'exit' or 'quit' to stop.")
    print("Type 'voice' to use microphone.\n")

    while True:
        user_query = input("Ask for a book recommendation: ").strip()

        if user_query.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        # 🎤 Voice mode
        if user_query.lower() == "voice":
            print("Recording for 5 seconds...")
            try:
                user_query = record_and_transcribe(5)
                print(f"\nTranscribed text:\n{user_query}\n")
            except Exception as exc:
                print("\nResponse:\n")
                print(f"Voice input failed: {exc}")
                print()
                continue

        # 🛑 Moderation
        if not is_safe(user_query):
            print("\nResponse:\n")
            print("Please use respectful language.")
            print()
            continue

        # 🤖 Chatbot
        result = ask_chatbot(user_query)

        response = result["text"]
        title = result["title"]

        print("\nResponse:\n")
        print(response)
        print()

        # 🔊 TTS
        listen = input("Do you want audio? (yes/no): ").strip().lower()
        if listen == "yes":
            speak(response)

        # 🎨 Image generation
        generate_img = input("Do you want an image? (yes/no): ").strip().lower()
        if generate_img == "yes" and title:
            try:
                image_path = generate_book_image(title)
                print(f"Image saved to: {image_path}")

                import os
                os.startfile(image_path)  # Windows

            except Exception as e:
                print(f"Image generation failed: {e}")

        print("-" * 50)


if __name__ == "__main__":
    main()