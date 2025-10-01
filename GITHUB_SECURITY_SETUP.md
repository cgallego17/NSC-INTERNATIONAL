# GitHub Security Setup Guide

## 🔒 Enabling GitHub Security Features

### 1. Enable Code Scanning

**Step 1: Go to Repository Settings**

1. Navigate to your GitHub repository
2. Click on **Settings** tab
3. Scroll down to **Security** section in the left sidebar

**Step 2: Enable Code Scanning**

1. Click on **Code security and analysis**
2. Find **Code scanning** section
3. Click **Set up** or **Enable** button
4. Choose **Set up this workflow** (recommended)

**Step 3: Configure Code Scanning**

- **Default setup**: Uses CodeQL analysis
- **Advanced setup**: Custom configuration
- **Actions permissions**: Allow GitHub Actions to read and write permissions

### 2. Enable Dependency Scanning

**In the same Security section:**

1. Find **Dependency graph**
2. Enable **Dependency graph** (if not already enabled)
3. Enable **Dependabot alerts** (optional but recommended)
4. Enable **Dependabot security updates** (optional but recommended)

### 3. Enable Secret Scanning

**In the Security section:**

1. Find **Secret scanning**
2. Enable **Secret scanning**
3. Enable **Push protection** (recommended)

## 🛠️ Manual Setup (Alternative)

If automatic setup doesn't work, you can manually enable:

### Enable Code Scanning via GitHub CLI

```bash
# Install GitHub CLI if not already installed
# Windows: winget install GitHub.cli
# macOS: brew install gh
# Linux: curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg

# Login to GitHub
gh auth login

# Enable code scanning for your repository
gh api repos/:owner/:repo/code-scanning/alerts --method GET
```

### Enable via Repository Settings API

```bash
# Enable code scanning
gh api repos/:owner/:repo/code-scanning/alerts --method POST \
  --field state=open \
  --field severity=medium
```

## 📋 Required Repository Permissions

### GitHub Actions Permissions

1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions**:
   - Select **Read and write permissions**
   - Check **Allow GitHub Actions to create and approve pull requests**

### Security Tab Access

1. Go to **Settings** → **Security**
2. Ensure you have **Admin** or **Maintain** permissions
3. Check that **Security** tab is visible in the repository

## 🔧 Troubleshooting

### Common Issues

#### 1. "Code scanning is not enabled"

**Solution**: Follow the steps above to enable code scanning in repository settings.

#### 2. "Insufficient permissions"

**Solution**:

- Ensure you have Admin or Maintain permissions
- Check GitHub Actions permissions
- Verify organization security policies

#### 3. "Security tab not visible"

**Solution**:

- Enable security features in repository settings
- Check organization security policies
- Ensure repository is public or you have appropriate access

#### 4. "SARIF upload fails"

**Solution**:

- Verify SARIF file format is valid
- Check that code scanning is enabled
- Ensure proper permissions are set

### Verification Steps

1. **Check Security Tab**:

   - Go to your repository
   - Click on **Security** tab
   - Verify **Code scanning** section is visible

2. **Check Actions Permissions**:

   - Go to **Settings** → **Actions** → **General**
   - Verify workflow permissions are set correctly

3. **Test SARIF Upload**:
   - Run a security workflow
   - Check if results appear in Security tab
   - Verify no upload errors in Actions logs

## 🚀 Quick Setup Script

Create a script to automate the setup:

```bash
#!/bin/bash
# setup-github-security.sh

REPO_OWNER="your-username"
REPO_NAME="NSC-INTERNATIONAL"

echo "Setting up GitHub Security for $REPO_OWNER/$REPO_NAME"

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI not found. Please install it first:"
    echo "Windows: winget install GitHub.cli"
    echo "macOS: brew install gh"
    echo "Linux: curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
    exit 1
fi

# Login to GitHub
echo "Please login to GitHub CLI:"
gh auth login

# Enable code scanning
echo "Enabling code scanning..."
gh api repos/$REPO_OWNER/$REPO_NAME/code-scanning/alerts --method GET || echo "Code scanning may already be enabled"

# Check repository settings
echo "Checking repository settings..."
gh api repos/$REPO_OWNER/$REPO_NAME

echo "Setup complete! Please verify in GitHub web interface:"
echo "1. Go to https://github.com/$REPO_OWNER/$REPO_NAME/settings/security"
echo "2. Enable Code scanning"
echo "3. Enable Dependency graph"
echo "4. Enable Secret scanning"
```

## 📊 Expected Results

After enabling code scanning, you should see:

1. **Security Tab** with sections:

   - Code scanning alerts
   - Dependency graph
   - Secret scanning alerts
   - Security advisories

2. **Actions Tab** with:

   - Security workflow runs
   - SARIF upload success messages
   - No permission errors

3. **Code Scanning Results**:
   - Bandit security issues
   - Safety vulnerability reports
   - Semgrep static analysis results
   - Trivy container scans

## 🔗 Useful Links

- [GitHub Code Scanning Documentation](https://docs.github.com/en/code-security/code-scanning)
- [SARIF Support for Code Scanning](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning)
- [GitHub Security Features](https://docs.github.com/en/code-security)
- [GitHub Actions Permissions](https://docs.github.com/en/actions/using-workflows/workflow-permissions)

## 📝 Next Steps

1. **Enable Code Scanning** in repository settings
2. **Run Security Workflows** to test
3. **Check Security Tab** for results
4. **Configure Alerts** for new vulnerabilities
5. **Set up Notifications** for security findings

---

**Note**: Some features may require GitHub Pro, Team, or Enterprise plans depending on your repository's visibility and organization settings.
