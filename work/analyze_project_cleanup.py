#!/usr/bin/env python3
"""
Project Cleanup Analysis
Identify unnecessary files for deletion and organize documentation.
"""

import os
from pathlib import Path
from collections import defaultdict
import re

def analyze_markdown_files(root_dir):
    """Analyze markdown documentation files."""
    md_files = list(Path(root_dir).glob('*.md'))
    
    categories = {
        'active': [],
        'obsolete_phase': [],
        'obsolete_batch': [],
        'obsolete_option': [],
        'superseded': [],
        'keep': []
    }
    
    for md_file in md_files:
        name = md_file.name
        
        # Active/Current documentation
        if name in ['README.md', 'ZWNJ_ROOT_CAUSE_ANALYSIS.md', 'ZWNJ_BREAKTHROUGH.md']:
            categories['keep'].append((md_file, 'Current active documentation'))
        
        # Obsolete Phase 1-5 docs
        elif re.match(r'PHASE[1-5]_', name):
            categories['obsolete_phase'].append((md_file, 'Old phase documentation (superseded)'))
        
        # Phase 6 Batch 1-4 (completed, can archive)
        elif re.match(r'PHASE6_BATCH[1-4]', name):
            categories['obsolete_batch'].append((md_file, 'Completed batch documentation'))
        
        # Option/Hybrid exploration docs (not used)
        elif re.match(r'(OPTION|HYBRID)', name):
            categories['obsolete_option'].append((md_file, 'Exploratory docs (not pursued)'))
        
        # Batch 2/3 exploration docs
        elif re.match(r'BATCH[2-3]_', name):
            categories['obsolete_batch'].append((md_file, 'Old batch exploration'))
        
        # Training status docs (outdated)
        elif name in ['TRAINING_STATUS.md', 'TRAINING_STATUS_NOW.md', 'TRAINING_PROGRESS.md']:
            categories['superseded'].append((md_file, 'Outdated training status'))
        
        # Other misc docs
        elif name in ['guideline.md', 'COMPLETE_GUIDE.md', 'QUICK_REFERENCE.md']:
            categories['superseded'].append((md_file, 'Generic guides (not updated)'))
        
        # Specific docs to review
        elif name in ['EVALUATION_RESULTS.md', 'PHASE6_STRATEGIC_PLAN.md', 'PHASE6_QUICKSTART.md']:
            categories['keep'].append((md_file, 'Useful reference documentation'))
        
        elif name in ['SCRAPER_INTEGRATION_GUIDE.md', 'ROOT_CAUSE_SOLUTION.md']:
            categories['keep'].append((md_file, 'Technical documentation'))
        
        # Encoding/ZWNJ problem docs
        elif name in ['ENCODING_ISSUES_RESOLVED.md', 'ZWNJ_PROBLEM_ANALYSIS.md']:
            categories['superseded'].append((md_file, 'Analysis superseded by ZWNJ_ROOT_CAUSE'))
        
        # Improvement plans (outdated)
        elif 'IMPROVE' in name or 'PLAN' in name:
            categories['superseded'].append((md_file, 'Old improvement plans'))
        
        else:
            categories['active'].append((md_file, 'Review needed'))
    
    return categories

def analyze_python_scripts(root_dir):
    """Analyze Python scripts."""
    work_dir = Path(root_dir) / 'work'
    
    categories = {
        'test_scripts': [],
        'debug_scripts': [],
        'analysis_tools': [],
        'scrapers': [],
        'keep': [],
        'obsolete': []
    }
    
    # Check work/ directory
    if work_dir.exists():
        for py_file in work_dir.glob('*.py'):
            name = py_file.name
            
            if name.startswith('test_'):
                categories['test_scripts'].append((py_file, 'Test/debug script'))
            elif 'debug' in name.lower():
                categories['debug_scripts'].append((py_file, 'Debug script'))
            elif name in ['check_phase4_quality.py', 'analyze_mgk_special_chars.py']:
                categories['analysis_tools'].append((py_file, 'Analysis tool (useful)'))
            elif name in ['verify_ckb_traineddata.py', 'kurdish_character_fixer.py']:
                categories['keep'].append((py_file, 'Utility script'))
            else:
                categories['obsolete'].append((py_file, 'Review needed'))
    
    # Check work/tools/
    tools_dir = work_dir / 'tools'
    if tools_dir.exists():
        for py_file in tools_dir.glob('*.py'):
            name = py_file.name
            
            if name.startswith('test_'):
                categories['test_scripts'].append((py_file, 'Test/debug script'))
            elif name in ['scrape_wikipedia_quality.py', 'scrape_from_urls.py']:
                categories['obsolete'].append((py_file, 'Old scraper (not used)'))
            else:
                categories['keep'].append((py_file, 'Active tool'))
    
    # Check work/corpus/
    corpus_dir = work_dir / 'corpus'
    if corpus_dir.exists():
        for py_file in corpus_dir.glob('*.py'):
            name = py_file.name
            
            if name in ['filter_high_zwnj.py', 'analyze_special_chars.py']:
                categories['keep'].append((py_file, 'Active analysis tool'))
            elif name.startswith('check_'):
                categories['analysis_tools'].append((py_file, 'Batch verification (archive)'))
            elif name.startswith('create_'):
                categories['analysis_tools'].append((py_file, 'Batch creation (archive)'))
            else:
                categories['obsolete'].append((py_file, 'Review needed'))
    
    return categories

def analyze_text_files(root_dir):
    """Analyze text files."""
    work_dir = Path(root_dir) / 'work'
    corpus_dir = work_dir / 'corpus'
    
    categories = {
        'training_corpus': [],
        'backup_corpus': [],
        'debug_files': [],
        'ground_truth': [],
        'misc': []
    }
    
    if corpus_dir.exists():
        for txt_file in corpus_dir.glob('*.txt'):
            name = txt_file.name
            
            if name.endswith('.training_text'):
                if 'backup' in name or 'phase' in name or 'old' in name:
                    categories['backup_corpus'].append((txt_file, 'Old corpus backup'))
                elif name in ['ckb_high_zwnj.training_text', 
                              'ckb_phase6_batch4.training_text',
                              'ckb_scraped_filtered.training_text',
                              'ckb_wikipedia_bio_filtered.training_text']:
                    categories['training_corpus'].append((txt_file, 'Active corpus'))
                else:
                    categories['backup_corpus'].append((txt_file, 'Old experimental corpus'))
            
            elif name.endswith('.txt'):
                if any(x in name for x in ['enhanced', 'expanded', 'extra', 'formats', 'coverage']):
                    categories['misc'].append((txt_file, 'Old experimental text'))
                elif 'phase' in name or 'batch' in name:
                    categories['backup_corpus'].append((txt_file, 'Old corpus file'))
                else:
                    categories['misc'].append((txt_file, 'Review needed'))
    
    # Check for debug template
    debug_file = Path(root_dir) / 'debug_template.txt'
    if debug_file.exists():
        categories['debug_files'].append((debug_file, 'Debug template'))
    
    return categories

def generate_cleanup_report(root_dir):
    """Generate comprehensive cleanup report."""
    
    print("="*80)
    print("PROJECT CLEANUP ANALYSIS")
    print("="*80)
    print()
    
    # Analyze markdown files
    print("📄 MARKDOWN DOCUMENTATION ANALYSIS")
    print("-"*80)
    md_categories = analyze_markdown_files(root_dir)
    
    total_md = 0
    for category, files in md_categories.items():
        if files:
            print(f"\n{category.upper().replace('_', ' ')} ({len(files)} files):")
            for file_path, reason in files:
                print(f"  • {file_path.name:<50} | {reason}")
                total_md += 1
    
    print(f"\nTotal markdown files: {total_md}")
    
    # Analyze Python scripts
    print("\n\n🐍 PYTHON SCRIPTS ANALYSIS")
    print("-"*80)
    py_categories = analyze_python_scripts(root_dir)
    
    total_py = 0
    for category, files in py_categories.items():
        if files:
            print(f"\n{category.upper().replace('_', ' ')} ({len(files)} files):")
            for file_path, reason in sorted(files)[:10]:  # Show first 10
                print(f"  • {file_path.name:<50} | {reason}")
                total_py += 1
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more")
    
    print(f"\nTotal Python files analyzed: {total_py}")
    
    # Analyze text files
    print("\n\n📝 TEXT FILES ANALYSIS")
    print("-"*80)
    txt_categories = analyze_text_files(root_dir)
    
    total_txt = 0
    for category, files in txt_categories.items():
        if files:
            print(f"\n{category.upper().replace('_', ' ')} ({len(files)} files):")
            for file_path, reason in sorted(files)[:10]:  # Show first 10
                print(f"  • {file_path.name:<50} | {reason}")
                total_txt += 1
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more")
    
    print(f"\nTotal text files analyzed: {total_txt}")
    
    # Generate recommendations
    print("\n\n📋 CLEANUP RECOMMENDATIONS")
    print("="*80)
    
    print("\n✅ FILES TO KEEP:")
    print("-"*80)
    print("Documentation:")
    print("  • README.md - Project overview")
    print("  • ZWNJ_ROOT_CAUSE_ANALYSIS.md - Root cause analysis (current)")
    print("  • ZWNJ_BREAKTHROUGH.md - Solution summary (current)")
    print("  • EVALUATION_RESULTS.md - Results reference")
    print("  • PHASE6_STRATEGIC_PLAN.md - Strategic planning")
    print("  • docs/kurdish_characters.md - Character reference")
    print("  • docs/PRODUCTION_READINESS.md - Deployment docs")
    
    print("\nScripts:")
    print("  • run_training.ps1 - Main training pipeline")
    print("  • work/corpus/filter_high_zwnj.py - High-ZWNJ filter")
    print("  • work/corpus/analyze_special_chars.py - Character analysis")
    print("  • work/analyze_mgk_special_chars.py - Test image analysis")
    print("  • work/tools/scrapers/* - Active scrapers")
    
    print("\nCorpus Files:")
    print("  • work/corpus/ckb_high_zwnj.training_text - Batch 5 corpus")
    print("  • work/corpus/ckb_phase6_batch4.training_text - Latest full corpus")
    print("  • work/corpus/ckb_scraped_filtered.training_text - News corpus")
    print("  • work/corpus/ckb_wikipedia_bio_filtered.training_text - Wikipedia corpus")
    
    print("\n\n🗑️  FILES TO DELETE/ARCHIVE:")
    print("-"*80)
    
    delete_count = (
        len(md_categories['obsolete_phase']) + 
        len(md_categories['obsolete_batch']) + 
        len(md_categories['obsolete_option']) +
        len(md_categories['superseded'])
    )
    
    print(f"\nMarkdown files to archive: ~{delete_count} files")
    print("  • PHASE1-5 documentation (40+ files)")
    print("  • PHASE6_BATCH1-4 detailed logs (10+ files)")
    print("  • OPTION/HYBRID exploration docs (6+ files)")
    print("  • Old training status docs (3+ files)")
    
    print(f"\nPython scripts to remove: ~{len(py_categories['test_scripts']) + len(py_categories['debug_scripts'])} files")
    print("  • test_*.py scripts (20+ files)")
    print("  • debug_*.py scripts (5+ files)")
    print("  • Old scraper experiments (5+ files)")
    
    print(f"\nText files to clean: ~{len(txt_categories['backup_corpus']) + len(txt_categories['misc'])} files")
    print("  • Old corpus backups (30+ files)")
    print("  • Experimental text files (20+ files)")
    print("  • Phase 1-5 corpus files (10+ files)")
    
    print("\n\n💾 STORAGE SAVINGS:")
    print("-"*80)
    print("  • Markdown docs: ~0.4 MB")
    print("  • Python scripts: ~2-3 MB")
    print("  • Old corpus files: ~50-60 MB")
    print("  • Total potential savings: ~53-63 MB")
    
    print("\n\n📦 RECOMMENDED STRUCTURE:")
    print("="*80)
    print("""
tesseract/
├── README.md                          # Project overview
├── ZWNJ_BREAKTHROUGH.md              # Current solution summary
├── ZWNJ_ROOT_CAUSE_ANALYSIS.md       # Technical analysis
├── EVALUATION_RESULTS.md             # Results reference
├── run_training.ps1                  # Training pipeline
├── docs/
│   ├── kurdish_characters.md         # Character reference
│   ├── PRODUCTION_READINESS.md       # Deployment guide
│   └── PHASE6_STRATEGIC_PLAN.md      # Strategic planning
├── archive/
│   ├── phase1-5/                     # Old phase docs (archived)
│   ├── batches/                      # Batch 1-4 docs (archived)
│   └── experiments/                  # Exploration docs (archived)
├── work/
│   ├── corpus/
│   │   ├── ckb_high_zwnj.training_text           # Batch 5 (active)
│   │   ├── ckb_phase6_batch4.training_text       # Latest full
│   │   ├── ckb_scraped_filtered.training_text    # News source
│   │   ├── ckb_wikipedia_bio_filtered.training_text  # Wikipedia
│   │   ├── filter_high_zwnj.py                   # Filter tool
│   │   └── analyze_special_chars.py              # Analysis tool
│   ├── tools/
│   │   └── scrapers/                 # Active scrapers only
│   └── analyze_mgk_special_chars.py  # Test analysis
└── tessdata/
    ├── best/ckb.traineddata          # Best model
    └── fast/ckb.traineddata          # Fast model
""")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Review this analysis")
    print("2. Create archive/ directory structure")
    print("3. Move obsolete files to archive/")
    print("4. Delete test/debug scripts")
    print("5. Clean up old corpus files")
    print("6. Update README.md with current status")
    print("7. Proceed with Batch 5 training")

if __name__ == '__main__':
    root_dir = Path(__file__).parent.parent
    generate_cleanup_report(root_dir)
