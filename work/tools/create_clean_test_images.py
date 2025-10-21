#!/usr/bin/env python3
"""
Create clean test images by rendering just the article text
Similar to how mgk.tif was created (clean text on white background)
"""
import subprocess
import os

def create_text_image(text_file, output_base):
    """Create a clean text image using ImageMagick"""
    
    # Read text
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    
    # Create temp file for ImageMagick
    temp_file = f'/tmp/{output_base}_temp.txt'
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    # Use ImageMagick to create clean text image
    # Similar settings to training data
    cmd = [
        'convert',
        '-size', '2480x3508',  # A4 size at 300 DPI
        '-background', 'white',
        '-fill', 'black',
        '-font', '/mnt/c/tesseract/work/fonts/NotoNaskhArabic-Bold.ttf',
        '-pointsize', '24',
        '-gravity', 'NorthWest',
        f'caption:@{temp_file}',
        '-trim',
        '+repage',
        f'/mnt/c/tesseract/work/real_gt/eval_clean/{output_base}.tif'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            # Check if file was created
            output_path = f'/mnt/c/tesseract/work/real_gt/eval_clean/{output_base}.tif'
            if os.path.exists(output_path):
                size = os.path.getsize(output_path) / 1024  # KB
                return True, f"{size:.1f}KB"
            return False, "File not created"
        else:
            return False, result.stderr[:100]
    except Exception as e:
        return False, str(e)[:100]

def main():
    print("="*70)
    print("🎨 Creating Clean Text Images (Like mgk.tif Style)")
    print("="*70)
    
    os.makedirs('/mnt/c/tesseract/work/real_gt/eval_clean', exist_ok=True)
    
    # Get all ground truth files from eval_multi
    gt_files = []
    eval_multi = '/mnt/c/tesseract/work/real_gt/eval_multi'
    for filename in os.listdir(eval_multi):
        if filename.endswith('.gt.txt'):
            gt_files.append(filename[:-7])  # Remove .gt.txt
    
    print(f"\n📋 Found {len(gt_files)} text files to render\n")
    
    success = 0
    for base_name in gt_files:
        gt_path = f'{eval_multi}/{base_name}.gt.txt'
        print(f"  Rendering {base_name}...", end=' ')
        
        # Copy GT file
        subprocess.run(['cp', gt_path, f'/mnt/c/tesseract/work/real_gt/eval_clean/{base_name}.gt.txt'])
        
        # Create image
        ok, msg = create_text_image(gt_path, base_name)
        if ok:
            print(f"✅ ({msg})")
            success += 1
        else:
            print(f"❌ {msg}")
    
    print(f"\n{'='*70}")
    print(f"✅ Successfully created {success}/{len(gt_files)} clean test images")
    print(f"{'='*70}\n")
    
    # List created files
    subprocess.run(['ls', '-lh', '/mnt/c/tesseract/work/real_gt/eval_clean/'])

if __name__ == '__main__':
    main()
