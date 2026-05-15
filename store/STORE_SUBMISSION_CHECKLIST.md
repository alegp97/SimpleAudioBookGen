# Microsoft Store Submission Checklist

## 1. Account & Preparation
- [ ] Register as a Microsoft App Developer (Partner Center).
- [ ] Reserve the name "SimpleAudioBookGen".
- [ ] Ensure `audiobook_gen/__init__.py` version matches the submission version.

## 2. Technical Requirements
- [ ] Build a clean, portable executable using `build.py`.
- [ ] Generate the Windows Installer (`SimpleAudioBookGen-Setup-x.x.x.exe`) using Inno Setup.
- [ ] **Important:** Test the installer on a clean Windows machine.
- [ ] Verify that the App starts from the Start Menu after installation.
- [ ] Ensure no administrator privileges are strictly required for the App to run.

## 3. Store Listing Assets
- [ ] Prepare 6 high-resolution screenshots (1920x1080).
- [ ] Prepare the App Icon (PNG, 512x512 and other required sizes).
- [ ] Copy text from `store/MICROSOFT_STORE_LISTING.md`.

## 4. Legal & Privacy
- [ ] Publish the content of `docs/PRIVACY_POLICY.md` to a public URL.
- [ ] Provide the Privacy Policy URL in the Partner Center.
- [ ] Fill out the Age Rating questionnaire (General Audience/3+).

## 5. Pricing & Distribution
- [ ] Set price to $0.99 USD.
- [ ] Select target countries/regions.
- [ ] Set release date.

## 6. Testing Checklist (Pre-submission)
- [ ] Convert a small text-based PDF.
- [ ] Convert a scanned PDF (requires OCR).
- [ ] Test "Natural Online" voice with internet.
- [ ] Test "Basic System" voice without internet.
- [ ] Verify MP3 output quality and metadata.
- [ ] Test the "Cancel" button during conversion.
