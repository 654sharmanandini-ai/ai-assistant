import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
import re

pdf_path = r"C:\Users\654sh\OneDrive\Desktop\Peace Corps Learner Guide to Pular.pdf"

reader = PdfReader(pdf_path)
pular_chars = set('åðýñøƀÅÐÝƁ')

def is_good_pular(line):
    line = line.strip()
    if len(line) < 4 or len(line) > 120:
        return False
    skip = ['......', 'livelingua', 'Hosted for', 'VOCABULARY', 'GRAMMAR',
            'EXERCISES', 'CULTURAL', 'Competence', 'COMPETENCE', 'KEY WORDS',
            'ANCIENT WISDOM', 'PLEASE NOTE', 'In this chapter', 'peace corps',
            'Peace Corps', 'Click', 'Table ', 'Figure ']
    if any(s in line for s in skip):
        return False
    has_pular = any(c in line for c in pular_chars)
    if not has_pular:
        return False
    eng_stopwords = {'the','this','that','with','from','have','been','they',
                    'their','there','which','would','could','should','about',
                    'because','however','although','therefore','when','where',
                    'some','more','than','then','also','only','even','just',
                    'very','most','many','much','each','both','such','these',
                    'were','was','had','has','are','and','but','for','not',
                    'into','upon','under','over','after','before','between',
                    'through','during','without','within','along','said',
                    'called','known','used','made','take','make','come',
                    'well','like','just','back','give','most','our','out'}
    words = [w.strip('.,!?:;()[]1234567890-').lower() for w in line.split()]
    words = [w for w in words if w]
    if not words:
        return False
    eng_count = sum(1 for w in words if w in eng_stopwords)
    if len(words) > 0 and eng_count / len(words) > 0.35:
        return False
    return True

# Extract from PDF pages 10-120
new_entries = []
seen = set()

for page_num in range(9, 120):
    text = reader.pages[page_num].extract_text()
    if not text:
        continue
    lines = text.split('\n')
    for j, line in enumerate(lines):
        line = line.strip()
        if not is_good_pular(line):
            continue
        if line in seen:
            continue
        seen.add(line)
        english = None
        if j + 1 < len(lines):
            next_line = lines[j+1].strip()
            next_has_pular = any(c in next_line for c in pular_chars)
            if (not next_has_pular and len(next_line) > 3 and
                len(next_line) < 100 and next_line not in seen):
                next_words = next_line.lower().split()
                eng_count = sum(1 for w in next_words
                               if w.strip('.,!?') in
                               {'i','you','he','she','we','is','are','the',
                                'to','a','in','of','it','my','your','his',
                                'peace','god','hello','yes','no','bye','thank',
                                'family','well','work','child','sleep','eat',
                                'drink','go','come','want','need','have','see'})
                if eng_count > 0:
                    english = next_line
        category = "general"
        line_lower = line.lower()
        if any(w in line_lower for w in ['jaraama','jam ','tanna','marsude','wa\'i']):
            category = "greetings"
        elif any(w in line_lower for w in ['jango','bimbi','ontuma','jemma','waalen']):
            category = "farewells"
        elif any(w in line_lower for w in ['ñaamugol','weelaa','ndiyan','maafe','ñaamdu']):
            category = "food"
        elif any(w in line_lower for w in ['selli','ñawii','ñawi','cellal']):
            category = "health"
        elif any(w in line_lower for w in ['njamndi','ðuytu','cewði','maakiti']):
            category = "shopping"
        elif any(w in line_lower for w in ['yahi','yahii','yahugol','woðði','suudu']):
            category = "travel"
        elif any(w in line_lower for w in ['baaba','nene','åeyngure','rewåe','woråe']):
            category = "family"
        elif any(w in line_lower for w in ['gol','ugol','aade','ude','itaade']):
            category = "verbs"
        new_entries.append({
            "pular": line,
            "english": english,
            "category": category
        })

print(f"New entries found: {len(new_entries)}")

# Add to existing ChromaDB
client = chromadb.PersistentClient(path="./pular_db")
ef = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_collection(name="pular_knowledge", embedding_function=ef)

existing_count = collection.count()
print(f"Existing entries: {existing_count}")

documents = []
metadatas = []
ids = []

for i, item in enumerate(new_entries):
    if item.get("english"):
        doc_text = f"Pular: {item['pular']} | Meaning: {item['english']} | Category: {item['category']}"
    else:
        doc_text = f"Pular: {item['pular']} | Category: {item['category']}"
    documents.append(doc_text)
    metadatas.append({
    	"pular": str(item["pular"]),
    	"english": str(item.get("english") or ""),
    	"category": str(item.get("category") or "general")
    })
    ids.append(f"pdf_{existing_count + i}")

batch_size = 50
for i in range(0, len(documents), batch_size):
    collection.add(
        documents=documents[i:i+batch_size],
        metadatas=metadatas[i:i+batch_size],
        ids=ids[i:i+batch_size]
    )
    print(f"  Added batch {i//batch_size + 1}")

print(f"\nTotal entries now: {collection.count()}")

# Test
results = collection.query(query_texts=["family greetings"], n_results=3)
print("\nTest - family greetings:")
for doc in results["documents"][0]:
    print(f"  -> {doc}")

print("\nDone! Knowledge base expanded!")