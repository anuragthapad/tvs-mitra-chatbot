import base64
import io
from PIL import Image
import pytesseract
import re
from typing import List, Dict, Any

class OCRChatbot:
    def __init__(self):
        self.extracted_text = ""
        self.text_sections = {}
        
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            # Open and process the image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using pytesseract
            extracted_text = pytesseract.image_to_string(image, lang='eng')
            
            # Clean up the text
            cleaned_text = self.clean_text(extracted_text)
            
            self.extracted_text = cleaned_text
            self.analyze_text_structure()
            
            return cleaned_text
            
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        text = text.strip()
        return text
    
    def analyze_text_structure(self):
        """Analyze text structure to identify sections"""
        lines = self.extracted_text.split('\n')
        current_section = "general"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Identify potential headers (all caps, short lines, etc.)
            if len(line) < 50 and (line.isupper() or ':' in line):
                current_section = line.lower().replace(':', '').strip()
                self.text_sections[current_section] = []
            else:
                if current_section not in self.text_sections:
                    self.text_sections[current_section] = []
                self.text_sections[current_section].append(line)
    
    def search_text(self, query: str) -> List[str]:
        """Search for relevant text based on query"""
        query_lower = query.lower()
        relevant_lines = []
        
        # Search through all text
        for line in self.extracted_text.split('\n'):
            if any(word in line.lower() for word in query_lower.split()):
                relevant_lines.append(line.strip())
        
        return relevant_lines[:5]  # Return top 5 matches
    
    def answer_question(self, question: str) -> str:
        """Generate answer based on extracted text"""
        if not self.extracted_text:
            return "No text has been extracted yet. Please process an image first."
        
        question_lower = question.lower()
        
        # Handle different types of questions
        if any(word in question_lower for word in ['what', 'describe', 'tell me about']):
            return self.describe_content()
        
        elif any(word in question_lower for word in ['find', 'search', 'look for']):
            # Extract search terms from question
            search_terms = question.replace('find', '').replace('search', '').replace('look for', '').strip()
            results = self.search_text(search_terms)
            if results:
                return f"Found the following relevant information:\n\n" + "\n".join(f"• {result}" for result in results)
            else:
                return f"No information found for '{search_terms}'"
        
        elif any(word in question_lower for word in ['how many', 'count', 'number']):
            return self.count_information(question)
        
        else:
            # General search based on question keywords
            results = self.search_text(question)
            if results:
                return f"Based on the document, here's what I found:\n\n" + "\n".join(f"• {result}" for result in results)
            else:
                return "I couldn't find specific information related to your question in the extracted text."
    
    def describe_content(self) -> str:
        """Provide a general description of the content"""
        if not self.extracted_text:
            return "No content available."
        
        word_count = len(self.extracted_text.split())
        line_count = len([line for line in self.extracted_text.split('\n') if line.strip()])
        
        description = f"Document Summary:\n"
        description += f"• Word count: {word_count}\n"
        description += f"• Lines of text: {line_count}\n\n"
        
        if self.text_sections:
            description += "Identified sections:\n"
            for section, content in self.text_sections.items():
                if content:
                    description += f"• {section.title()}: {len(content)} items\n"
        
        # Show first few lines as preview
        preview_lines = self.extracted_text.split('\n')[:3]
        description += f"\nContent preview:\n"
        for line in preview_lines:
            if line.strip():
                description += f"• {line.strip()}\n"
        
        return description
    
    def count_information(self, question: str) -> str:
        """Count specific items in the text"""
        question_lower = question.lower()
        
        if 'word' in question_lower:
            count = len(self.extracted_text.split())
            return f"The document contains {count} words."
        
        elif 'line' in question_lower:
            count = len([line for line in self.extracted_text.split('\n') if line.strip()])
            return f"The document contains {count} lines of text."
        
        elif 'section' in question_lower:
            count = len(self.text_sections)
            return f"The document has {count} identified sections."
        
        else:
            return "I can count words, lines, or sections. Please specify what you'd like me to count."

def main():
    print("🤖 OCR Chatbot - Extract text from images and ask questions!")
    print("=" * 60)
    
    chatbot = OCRChatbot()
    
    # Process the uploaded image
    image_path = "/tmp/uploaded_image.png"  # This will be the uploaded image
    
    print("📸 Processing uploaded image...")
    extracted_text = chatbot.extract_text_from_image(image_path)
    
    if "Error" in extracted_text:
        print(f"❌ {extracted_text}")
        return
    
    print("✅ Text extraction completed!")
    print(f"📄 Extracted {len(extracted_text.split())} words from the image.")
    print("\n" + "="*60)
    print("EXTRACTED TEXT:")
    print("="*60)
    print(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
    print("="*60)
    
    # Interactive chatbot loop
    print("\n💬 Ask me questions about the extracted text!")
    print("Type 'quit' to exit, 'show text' to see full text, or 'help' for commands.")
    
    while True:
        try:
            question = input("\n🔍 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            elif question.lower() in ['show text', 'full text', 'text']:
                print("\n📄 Full extracted text:")
                print("-" * 40)
                print(chatbot.extracted_text)
                print("-" * 40)
                continue
            
            elif question.lower() in ['help', 'commands']:
                print("\n📋 Available commands:")
                print("• Ask any question about the content")
                print("• 'show text' - Display full extracted text")
                print("• 'describe' - Get document summary")
                print("• 'find [term]' - Search for specific terms")
                print("• 'how many words/lines' - Count information")
                print("• 'quit' - Exit the chatbot")
                continue
            
            elif not question:
                print("Please enter a question or command.")
                continue
            
            # Get answer from chatbot
            answer = chatbot.answer_question(question)
            print(f"\n🤖 Answer: {answer}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
