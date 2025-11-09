# Deploying to Vercel

This guide will help you deploy your MICE Imputation tool to Vercel for free hosting.

## Prerequisites

- A GitHub/GitLab/Bitbucket account (recommended) OR Vercel CLI
- Node.js installed (for Vercel CLI)

## Method 1: Deploy via Vercel Dashboard (Easiest)

### Step 1: Create a Git Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Initialize git in your project:
```bash
cd "/Users/ARUN/Desktop/MICE TECHNIQUE"
git init
git add .
git commit -m "Initial commit: MICE Imputation Tool"
```

3. Push to GitHub:
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Vercel

1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click "Add New Project"
3. Import your GitHub repository
4. Vercel will auto-detect the settings
5. Click "Deploy"
6. Wait for deployment to complete (2-3 minutes)
7. Your app will be live at `https://your-project.vercel.app`

## Method 2: Deploy via Vercel CLI

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login

```bash
vercel login
```

Follow the authentication steps in your browser.

### Step 3: Deploy

```bash
cd "/Users/ARUN/Desktop/MICE TECHNIQUE"
vercel
```

Follow the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Select your account
- **Link to existing project?** No
- **Project name?** mice-imputation (or your preferred name)
- **Directory?** ./ (press Enter)
- **Override settings?** No

Vercel will:
1. Upload your files
2. Build the project
3. Deploy to production
4. Give you a live URL

### Step 4: Deploy Updates

After making changes:
```bash
vercel --prod
```

## Configuration

The `vercel.json` file configures how Vercel handles your app:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/$1.py"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ]
}
```

This configuration:
- Builds Python files in the `api/` directory as serverless functions
- Routes `/api/upload` to `api/upload.py`
- Routes `/api/health` to `api/health.py`
- Serves static files (HTML, CSS, JS) directly

## Environment Variables (if needed)

If you need to add environment variables:

1. Go to your project on Vercel Dashboard
2. Settings → Environment Variables
3. Add your variables
4. Redeploy

## Custom Domain (Optional)

1. Go to your project on Vercel Dashboard
2. Settings → Domains
3. Add your custom domain
4. Follow DNS configuration instructions

## Limits on Vercel Free Tier

- **Serverless Function Timeout**: 10 seconds
- **Serverless Function Size**: 50MB (enough for our dependencies)
- **Bandwidth**: 100GB/month
- **Deployments**: Unlimited

For larger files or longer processing times, consider upgrading to Vercel Pro.

## Troubleshooting

### Build Fails

Check that:
- `requirements.txt` is present
- All imports are correct
- No syntax errors in Python files

### API Not Working

- Check browser console for errors
- Verify API routes match in `vercel.json`
- Test the health endpoint: `https://your-app.vercel.app/api/health`

### Large File Processing Issues

If processing takes > 10 seconds:
- Reduce file size
- Reduce number of iterations
- Consider upgrading to Vercel Pro (60s timeout)

## Monitoring

View logs in Vercel Dashboard:
1. Go to your project
2. Click on a deployment
3. View "Functions" tab for serverless logs

## Redeploying

Vercel automatically redeploys when you push to your Git repository (if connected via GitHub).

Or manually:
```bash
vercel --prod
```

## Getting Help

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Discord](https://vercel.com/discord)
- Check deployment logs in Vercel Dashboard
