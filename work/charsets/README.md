# Charsets (optional)

This folder is optional. If you populate it with the following files, the training pipeline will use them instead of downloading from upstream:

Required files to take effect:

- `Arabic.unicharset`
- `Latin.unicharset`
- `Common.unicharset`

Optional extras:

- `radical-stroke.txt`

If these files are missing, `execute_ckb_training.sh` will download the needed assets into `training_output/tmp/script` automatically.
