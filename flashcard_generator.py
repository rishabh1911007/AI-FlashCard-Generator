# flashcard_generator.py - AI-enabled version

import json
import re
import os

# Global variables for model (will be None if not loaded)
tokenizer = None
model = None


def load_ai_model():
    """Try to load AI model, return True if successful"""
    global tokenizer, model

    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM

        # Try multiple model options
        model_options = [
            "microsoft/DialoGPT-small",  # Smaller, more reliable
            "microsoft/phi-1_5",
            "distilgpt2"  # Very small fallback
        ]

        for model_name in model_options:
            try:
                print(f"Attempting to load model: {model_name}")

                tokenizer = AutoTokenizer.from_pretrained(model_name)
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token

                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                )
                model.eval()

                print(f"Successfully loaded: {model_name}")
                return True

            except Exception as e:
                print(f"Failed to load {model_name}: {str(e)}")
                continue

    except ImportError as e:
        print(f"Required libraries not available: {str(e)}")

    except Exception as e:
        print(f"Model loading failed: {str(e)}")

    return False


def generate_flashcards(text, difficulty="Easy"):
    """Generate flashcards with AI if available, otherwise use simple method"""

    print(f"Generating flashcards with difficulty: {difficulty}")
    print(f"Text length: {len(text)} characters")

    # Try AI generation first
    if model is not None and tokenizer is not None:
        try:
            flashcards = generate_ai_flashcards(text, difficulty)
            if flashcards and len(flashcards) > 0:
                print(f"AI generated {len(flashcards)} flashcards")
                return flashcards
        except Exception as e:
            print(f"AI generation failed: {str(e)}")

    # Fallback to simple generation
    print("Using simple flashcard generation")
    return create_simple_flashcards(text, difficulty)


def generate_ai_flashcards(text, difficulty):
    """Generate flashcards using AI model"""

    # Truncate text if too long
    if len(text) > 1200:
        text = text[:1200] + "..."

    prompt = f"""Create 10 flashcards from this text. Format as JSON array:
[{{"question": "What is...?", "answer": "...", "difficulty": "{difficulty}"}}]

Text: {text}

JSON:"""

    try:
        inputs = tokenizer(prompt, return_tensors="pt",
                           truncation=True, max_length=512)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=400,
                temperature=0.3,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response[len(prompt):].strip()

        print(f"AI Response: {response}")

        # Try to parse JSON
        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                flashcards = json.loads(json_str)

                # Validate flashcards
                valid_cards = []
                for card in flashcards:
                    if isinstance(card, dict) and "question" in card and "answer" in card:
                        card["difficulty"] = difficulty
                        valid_cards.append(card)

                if valid_cards:
                    return valid_cards
        except:
            pass

    except Exception as e:
        print(f"AI generation error: {str(e)}")

    return None


def create_simple_flashcards(text, difficulty):
    """Create simple flashcards from text without AI"""

    # Clean and split text into sentences
    sentences = text.replace('\n', ' ').split('.')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    # Also split on other punctuation to get more content
    additional_splits = []
    for sentence in sentences:
        parts = re.split(r'[;!?]', sentence)
        additional_splits.extend([p.strip()
                                 for p in parts if len(p.strip()) > 15])

    # Combine and deduplicate
    all_content = list(set(sentences + additional_splits))
    all_content = [s for s in all_content if len(s.strip()) > 15]

    flashcards = []

    # Create different types of questions based on difficulty
    if difficulty == "Easy":
        question_templates = [
            "What is mentioned about {}?",
            "According to the text, what can you say about {}?",
            "What does the document say regarding {}?",
            "What is {}?",
            "How is {} described?",
            "What information is given about {}?",
            "What does the text tell us about {}?",
            "What is the main point about {}?",
            "What can we learn about {}?",
            "What is stated regarding {}?"
        ]
    elif difficulty == "Medium":
        question_templates = [
            "How does {} relate to the main topic?",
            "What are the key points about {}?",
            "Explain the significance of {}.",
            "What is the relationship between {} and other concepts?",
            "How would you summarize the information about {}?",
            "What conclusions can be drawn about {}?",
            "What is the importance of {}?",
            "How does {} contribute to the overall understanding?",
            "What are the implications of {}?",
            "How does {} connect to the broader context?"
        ]
    else:  # Hard
        question_templates = [
            "Analyze the relationship between {} and other concepts.",
            "What are the implications of {}?",
            "How would you evaluate the importance of {}?",
            "What are the underlying principles behind {}?",
            "How does {} challenge or support existing knowledge?",
            "What are the broader consequences of {}?",
            "How would you critically assess {}?",
            "What are the theoretical foundations of {}?",
            "How does {} fit into the larger framework?",
            "What are the potential applications of {}?"
        ]

    # Generate flashcards from content
    for i, content in enumerate(all_content[:10]):  # Limit to 10 flashcards
        try:
            # Extract key terms (improved approach)
            words = re.findall(r'\b[A-Za-z]{4,}\b', content)
            # Filter out common words
            common_words = {'that', 'this', 'with', 'have', 'will', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'many', 'some', 'more', 'very', 'what', 'know', 'just', 'first', 'into', 'over', 'think', 'also',
                            'your', 'work', 'life', 'only', 'can', 'still', 'should', 'after', 'being', 'now', 'made', 'before', 'here', 'through', 'when', 'where', 'much', 'same', 'right', 'used', 'take', 'three', 'want', 'does', 'get'}
            key_terms = [word for word in words if word.lower(
            ) not in common_words and len(word) > 4]

            if key_terms:
                key_term = key_terms[0]  # Use first significant word
                template = question_templates[i % len(question_templates)]
                question = template.format(key_term)
            else:
                # Fallback questions when no key terms found
                fallback_questions = [
                    "What is the main point of this statement?",
                    "What information is provided here?",
                    "What does this text explain?",
                    "What is being described?",
                    "What is the key message?",
                    "What concept is presented?",
                    "What idea is conveyed?",
                    "What is being discussed?",
                    "What topic is covered?",
                    "What subject is addressed?"
                ]
                question = fallback_questions[i % len(fallback_questions)]

            flashcard = {
                "question": question,
                "answer": content.strip(),
                "difficulty": difficulty
            }

            flashcards.append(flashcard)

        except Exception as e:
            print(f"Error creating flashcard {i}: {str(e)}")
            continue

    # If we don't have enough flashcards, create additional ones from the text
    while len(flashcards) < 10 and len(text) > 50:
        try:
            # Split text into chunks and create general questions
            chunk_size = len(text) // (10 - len(flashcards))
            start_idx = len(flashcards) * chunk_size
            chunk = text[start_idx:start_idx + min(chunk_size, 200)]

            general_questions = [
                "What is discussed in this section?",
                "What information is presented here?",
                "What key points are mentioned?",
                "What concepts are explained?",
                "What details are provided?",
                "What topics are covered?",
                "What ideas are presented?",
                "What is the focus of this content?",
                "What subject matter is addressed?",
                "What themes are explored?"
            ]

            question = general_questions[len(
                flashcards) % len(general_questions)]

            flashcard = {
                "question": question,
                "answer": chunk.strip(),
                "difficulty": difficulty
            }

            flashcards.append(flashcard)

        except Exception as e:
            print(f"Error creating additional flashcard: {str(e)}")
            break

    # Ensure we have at least one flashcard
    if not flashcards:
        flashcards = [{
            "question": "What is the main topic of this document?",
            "answer": text[:200] + "..." if len(text) > 200 else text,
            "difficulty": difficulty
        }]

    return flashcards[:10]  # Ensure we return exactly 10 or fewer


# Try to load AI model when module is imported
print("Loading flashcard generator...")
ai_loaded = load_ai_model()
if ai_loaded:
    print("✅ AI model loaded successfully")
else:
    print("⚠️ AI model not loaded, using simple generation")

# Test function
if __name__ == "__main__":
    test_text = "Artificial intelligence is transforming many industries. Machine learning algorithms can process vast amounts of data. Deep learning models use neural networks to make predictions. Natural language processing enables computers to understand human language. Computer vision allows machines to interpret visual information. Robotics combines AI with physical systems. Expert systems capture human knowledge. Neural networks mimic brain structures. Supervised learning uses labeled data. Unsupervised learning finds patterns in unlabeled data."
    result = generate_flashcards(test_text, "Easy")
    print(f"\nGenerated {len(result)} flashcards:")
    for i, card in enumerate(result, 1):
        print(f"{i}. Q: {card['question']}")
        print(f"   A: {card['answer']}")
        print()
