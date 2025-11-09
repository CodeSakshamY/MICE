# Deploy to Render (Recommended)

Render is the best option for deploying this MICE Imputation tool because it handles Python ML libraries without size limits.

## Why Render Instead of Vercel?

- ✅ No 50MB serverless function limit (Vercel's limit)
- ✅ scikit-learn + pandas work perfectly
- ✅ Longer processing times allowed
- ✅ Easier setup for Python apps
- ✅ Free tier with 750 hours/month

## Step-by-Step Deployment

### 1. Push Your Code to GitHub

```bash
cd "/Users/ARUN/Desktop/MICE TECHNIQUE"

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: MICE Imputation Tool"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/mice-imputation.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Render

1. Go to https://render.com and sign up (free)

2. Click "New +" → "Web Service"

3. Connect your GitHub account

4. Select your `mice-imputation` repository

5. Render will detect it's a Python app. Configure:
   - **Name**: `mice-imputation` (or any name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: `Free`

6. Click "Create Web Service"

7. Wait 5-10 minutes for deployment (first time takes longer)

8. Your app will be live at: `https://mice-imputation.onrender.com`

## 3. Update Your Frontend (Optional)

If you want the frontend to use the Render URL automatically, update `script.js`:

```javascript
const API_URL = 'https://mice-imputation.onrender.com';
```

Or keep it auto-detecting:
```javascript
const API_URL = window.location.hostname === 'localhost' ? 'http://localhost:5000' : '';
```

## Testing Your Deployment

1. Visit: `https://your-app-name.onrender.com`
2. You should see the beautiful MICE interface
3. Upload an Excel file with missing values
4. Process and download!

## Troubleshooting

### Build Fails
- Check "Logs" tab in Render dashboard
- Make sure `requirements.txt` is present
- Verify Python version compatibility

### App Doesn't Start
- Check if port is set correctly (Render uses PORT environment variable)
- Look at runtime logs in Render dashboard

### API Not Responding
- Verify the health endpoint: `https://your-app.onrender.com/health`
- Should return: `{"status": "healthy", "message": "MICE Imputation API is running"}`

## Free Tier Limitations

- App "spins down" after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds to wake up
- 750 free hours per month
- Upgrade to paid ($7/month) for always-on

## Custom Domain (Optional)

1. In Render dashboard → Your service → Settings
2. Click "Custom Domain"
3. Add your domain
4. Update DNS settings as instructed

## Automatic Deployments

Once connected to GitHub:
- Every `git push` automatically deploys
- No manual steps needed
- See deployment status in Render dashboard

## Your App is Now Live! 🎉

Share your link: `https://your-app-name.onrender.com`

The MICE Imputation tool is now accessible to anyone with the URL!
