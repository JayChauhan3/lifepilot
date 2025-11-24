# Resend Email Service Setup

## Quick Start

1. **Sign up for Resend**
   - Go to https://resend.com
   - Create a free account (3,000 emails/month)

2. **Get your API key**
   - Go to https://resend.com/api-keys
   - Click "Create API Key"
   - Copy the key (starts with `re_`)

3. **Add to your `.env` file**
   ```bash
   # Email Service (Resend)
   RESEND_API_KEY=re_your_api_key_here
   RESEND_FROM_EMAIL=onboarding@resend.dev
   ```

4. **For production: Verify your domain**
   - Go to https://resend.com/domains
   - Add your domain (e.g., `yourdomain.com`)
   - Follow DNS verification steps
   - Update `RESEND_FROM_EMAIL` to use your domain (e.g., `noreply@yourdomain.com`)

## Testing

### Development Mode (No API Key)
If `RESEND_API_KEY` is not set, emails will be logged to console:
```
📧 MOCK EMAIL (No Resend API key) to=user@example.com link=http://...
```

### With Resend API Key
Emails will be sent to actual inboxes:
```
✅ Verification email sent to=user@example.com email_id=abc123
```

## Email Template

The verification email includes:
- Professional HTML design
- "Verify Email Address" button
- Clickable verification link
- 15-minute expiration notice
- LifePilot branding

## Troubleshooting

**Emails not sending?**
1. Check API key is correct in `.env`
2. Restart backend server after adding env vars
3. Check Resend dashboard for errors
4. Verify "from" email is allowed (use `onboarding@resend.dev` for testing)

**Using custom domain?**
1. Domain must be verified in Resend dashboard
2. DNS records must be properly configured
3. Wait up to 24 hours for DNS propagation
