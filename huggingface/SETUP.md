# Weekly Hugging Face sync setup

Target: https://huggingface.co/datasets/GarethFW/Accessible_Film_TV_and_Video_Content_Production_Management

1. Open [Actions variables](https://github.com/Double-FW/Accessible-Film-TV-and-Video-Content-Production-Management/settings/variables/actions). Add or edit the ordinary variable `HF_DATASET_ID` with value `GarethFW/Accessible_Film_TV_and_Video_Content_Production_Management`. This is not a token or full URL.
2. Open https://huggingface.co/settings/tokens and create a fine-grained/Custom token. Select only `GarethFW/Accessible_Film_TV_and_Video_Content_Production_Management` under repository permissions and grant read and write access. Leave unrelated user, inference and billing permissions unticked. Copy the token privately.
3. Open [Actions secrets](https://github.com/Double-FW/Accessible-Film-TV-and-Video-Content-Production-Management/settings/secrets/actions). Add or update `HF_TOKEN` (underscore) with that token. Never put it in source files, variables, documentation or chat.
4. Open [the workflow](https://github.com/Double-FW/Accessible-Film-TV-and-Video-Content-Production-Management/actions/workflows/huggingface-sync.yml), choose Run workflow with main and run. Open the result and inspect the publishing step, then the destination Files tab. Setup is complete only after a verified successful publication.

Configured schedule: Monday 09:53 UTC (09:53 UK winter; 10:53 UK summer). GitHub can delay scheduled runs and disable schedules in inactive public repositories. Manual Run workflow remains available.

The workflow checks committed source integrity, documentation, exact destination and approved MIT bytes. Only the publishing step receives HF_TOKEN. Source must be public; destination must already exist. Nine managed dataset files are updated in one commit guarded by the destination revision. Unrelated files, including `.gitattributes`, and repository visibility are preserved. A no-change run creates no destination commit. Concurrent destination changes stop publication rather than being blindly overwritten.

The export contains nine maintained documents and eight activities with 16 illustrative prompts. It preserves source authority and rights qualifications and copies the public repository register without renewing its verification dates. It does not fetch linked repository bodies, re-evaluate legal duties, train models or implement production controls. The allowlist is explicit: review additions to source or dataset structure before adding new files to the export configuration.

For local verification: `python scripts/check_documentation.py`, install `huggingface/requirements.txt`, then `python -m unittest discover -s tests -v`. Build with `python scripts/export_huggingface.py --output /tmp/media-preview --dataset-id GarethFW/Accessible_Film_TV_and_Video_Content_Production_Management`. Tests use a simulated publishing destination and no real token.
