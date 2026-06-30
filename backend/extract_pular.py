from pypdf import PdfReader
import json

def extract_pular_content(pdf_path):
    reader = PdfReader(pdf_path)
    results = []
    
    # These are clearly Pular sentence starters/patterns
    pular_starters = ['a ', 'on ', 'mi ', 'ko ', 'no ', 'en ', 'åe ', 'men ',
                      'an ', 'min ', 'awa', 'hii', 'o\'o', 'jam', 'tanna',
                      'hiða', 'miðo', 'si alla', 'åeyngure', 'ñallen',
                      'waalen', 'hiiren', 'honno', 'honto', 'honðun']
    
    pular_chars = ['å', 'ð', 'ý', 'ñ', 'ƀ', 'Å', 'Ð', 'Ý']
    
    # Words that confirm it's English text
    english_only = ['the ', 'this is', 'that is', 'there are', 'they are',
                   'it is a', 'in the', 'of the', 'to the', 'and the',
                   'for the', 'with the', 'from the', 'have been',
                   'has been', 'were ', 'would ', 'could ', 'should ',
                   'however', 'although', 'because', 'therefore',
                   'introduction', 'chapter', 'exercise', 'vocabulary',
                   'grammar note', 'cultural note', 'hosted for',
                   'livelingua', 'peace corps', 'phrasebook',
                   'competence', 'in this chapter', 'key words']
    
    print(f"Total pages: {len(reader.pages)}")
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue
        
        lines = text.split('\n')
        
        for j, line in enumerate(lines):
            line = line.strip()
            
            if not line or len(line) < 3:
                continue
            
            # Skip dots (table of contents)
            if '......' in line:
                continue
                
            # Skip livelingua watermark
            if 'livelingua' in line.lower():
                continue
            
            # Check if English only
            line_lower = line.lower()
            is_english = any(e in line_lower for e in english_only)
            if is_english:
                continue
            
            # Must have Pular special characters
            has_pular_char = any(c in line for c in pular_chars)
            
            # OR must start with Pular word and be short (likely a phrase)
            starts_with_pular = any(line_lower.startswith(s) for s in pular_starters)
            is_short_phrase = len(line) < 80
            
            if not has_pular_char and not (starts_with_pular and is_short_phrase):
                continue
            
            # Get English translation from next line if available
            english = None
            if j + 1 < len(lines):
                next_line = lines[j + 1].strip()
                next_has_pular = any(c in next_line for c in pular_chars)
                next_lower = next_line.lower()
                
                # Next line looks like English translation
                has_eng_words = any(e in next_lower for e in 
                                   ['i ', 'you ', 'he ', 'she ', 'we ', 'is ', 
                                    'are ', 'the ', 'to ', 'a ', 'in ', 'of ',
                                    'peace', 'god', 'family', 'hello', 'yes',
                                    'no ', 'bye', 'see you', 'thank'])
                
                if next_line and not next_has_pular and has_eng_words and len(next_line) < 100:
                    english = next_line
            
            results.append({
                "pular": line,
                "english": english,
                "page": i + 1
            })
    
    return results

# Run
pdf_path = r"C:\Users\654sh\OneDrive\Desktop\Peace Corps Learner Guide to Pular.pdf"
pairs = extract_pular_content(pdf_path)

print(f"\nExtracted {len(pairs)} Pular entries")
print("\nSample entries:")
for p in pairs[:40]:
    print(f"Pular: {p['pular']}")
    if p['english']:
        print(f"English: {p['english']}")
    print()

# Save
with open('pular_knowledge.json', 'w', encoding='utf-8') as f:
    json.dump(pairs, f, ensure_ascii=False, indent=2)

print(f"\nSaved {len(pairs)} entries to pular_knowledge.json!")