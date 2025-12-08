# 🔧 Quick Setup Guide - Using .env File

## Step 1: Create .env File

Run the setup script:
```bash
.\setup_env.bat
```

This will:
1. Copy `.env.example` to `.env`
2. Open the file in Notepad

## Step 2: Add Your API Key

1. Get your API key from [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys)
2. In the `.env` file, replace `your_fal_api_key_here` with your actual key
3. Save and close the file

Your `.env` file should look like:
```
FAL_KEY=fal_abc123xyz456...
```

## Step 3: Start the Server

```bash
.\start.bat
```

That's it! The server will automatically load your API key from the `.env` file.

---

## Alternative: Manual Setup

If you prefer to set up manually:

1. **Copy the example file:**
   ```bash
   copy .env.example .env
   ```

2. **Edit .env:**
   ```bash
   notepad .env
   ```

3. **Add your API key:**
   ```
   FAL_KEY=your_actual_api_key_here
   ```

4. **Save and start:**
   ```bash
   .\start.bat
   ```

---

## Troubleshooting

### "WARNING: .env file not found!"
**Solution:** Run `.\setup_env.bat` to create the file

### "FAL_KEY environment variable not set"
**Solution:** Make sure your `.env` file contains `FAL_KEY=your_key` (no quotes, no spaces around =)

### Changes not taking effect
**Solution:** Restart the server after editing `.env`

---

## Security Note

⚠️ **Never commit your `.env` file to version control!**

The `.env` file is already in `.gitignore` to prevent accidental commits.
