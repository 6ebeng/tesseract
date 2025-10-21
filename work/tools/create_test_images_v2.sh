#!/bin/bash
# Create test images by rendering Kurdish text to images using tesstrain approach

cd /mnt/c/tesseract/work

echo "======================================================================"
echo "Creating Test Images from News Corpus Samples"
echo "======================================================================"

mkdir -p real_gt/eval_synthetic

echo ""
echo "📝 Step 1: Extract text samples..."

# Create 5 diverse samples
python3 << 'PYTHON_SCRIPT'
# Extract different types of sentences from corpus
with open('corpus/kurdish_news_batch2.txt', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]

# Sample 1: Short sentences (10-15 words) - easier
short = [l for l in lines if 10 <= len(l.split()) <= 15][:20]

# Sample 2: Medium sentences (16-20 words) - moderate  
medium = [l for l in lines if 16 <= len(l.split()) <= 20][:20]

# Sample 3: Longer sentences (21-25 words) - harder
longer = [l for l in lines if 21 <= len(l.split()) <= 25][:20]

# Sample 4: Mixed from Kurdsat (political)
kurdsat = [l for l in lines[0:500]][:20]

# Sample 5: Mixed from Rudaw (diverse)
rudaw = [l for l in lines[500:1000]][:20]

samples = {
    'short': short,
    'medium': medium, 
    'long': longer,
    'kurdsat': kurdsat,
    'rudaw': rudaw
}

for name, sents in samples.items():
    with open(f'real_gt/eval_synthetic/{name}.gt.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(sents))
    print(f"  ✅ {name}.gt.txt: {len(sents)} sentences")

PYTHON_SCRIPT

echo ""
echo "📷 Step 2: Generate images using tesstrain tools..."
echo ""

# Use the same font config and settings as training
export FONTCONFIG_FILE=/mnt/c/tesseract/fonts.conf

for sample in short medium long kurdsat rudaw; do
    echo "  Generating ${sample}.tif..."
    
    # Use generate_line_images_from_text like training does
    timeout 60 python3 << PYTHON_SCRIPT
import subprocess
import os

text_file = 'real_gt/eval_synthetic/${sample}.gt.txt'
output_base = 'real_gt/eval_synthetic/${sample}'

# Read text
with open(text_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Create a temporary training file
with open(f'{output_base}.training_text', 'w', encoding='utf-8') as f:
    f.write(text)

# Generate using training tools
cmd = [
    'text2image',
    '--text=' + f'{output_base}.training_text',
    '--outputbase=' + output_base,
    '--font=Noto Naskh Arabic Bold',
    '--fonts_dir=fonts',
    '--ptsize=18',
    '--resolution=300',
    '--char_spacing=1.0',
    '--leading=22',
    '--exposure=0'
]

try:
    result = subprocess.run(cmd, cwd='/mnt/c/tesseract/work', 
                          capture_output=True, text=True, timeout=50)
    if result.returncode == 0:
        print(f"    ✅ Success")
    else:
        # Try alternative - use convert to create simple image
        print(f"    ⚠️  text2image failed, using ImageMagick fallback...")
        
        # Fallback: create simple text image with ImageMagick
        convert_cmd = [
            'convert',
            '-size', '2000x3000',
            '-background', 'white',
            '-fill', 'black',
            '-font', 'fonts/NotoNaskhArabic-Bold.ttf',
            '-pointsize', '24',
            f'label:@{output_base}.training_text',
            f'{output_base}.tif'
        ]
        result2 = subprocess.run(convert_cmd, cwd='/mnt/c/tesseract/work',
                               capture_output=True, text=True, timeout=30)
        if result2.returncode == 0:
            print(f"    ✅ Fallback succeeded")
        else:
            print(f"    ❌ Both methods failed")
except Exception as e:
    print(f"    ❌ Error: {e}")

PYTHON_SCRIPT

done

echo ""
echo "======================================================================"
echo "Test Images Status"
echo "======================================================================"
ls -lh real_gt/eval_synthetic/*.tif 2>/dev/null || echo "No .tif files created"

echo ""
echo "If image generation failed, we'll use alternative approach..."
