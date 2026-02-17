# RapidAPI Setup Guide for EditPDFree PDF API

This guide walks you through listing the EditPDFree PDF API on RapidAPI Hub.

## Prerequisites

- Active RapidAPI Provider account (create at https://rapidapi.com/provider)
- Access to https://api.editpdfree.com
- OpenAPI spec file (openapi.yaml in this directory)

## Step 1: Create RapidAPI Provider Account

1. Go to https://rapidapi.com/provider
2. Click "Sign Up" or "Get Started"
3. Complete registration with email verification
4. Set up your provider profile:
   - Provider name: "EditPDFree" or your company name
   - Description: Professional PDF processing solutions
   - Logo: Upload your logo (recommended size: 400x400px)
   - Website: https://www.editpdfree.com

## Step 2: Add New API

1. Log in to RapidAPI Provider Dashboard
2. Click "Add New API" button
3. Choose "Import from OpenAPI Spec"
4. Upload the `openapi.yaml` file from this directory

## Step 3: Configure API Details

### Basic Information
- **API Name**: EditPDFree PDF API
- **Short Description**: Professional PDF manipulation API: Convert HTML/URLs to PDF, merge, compress, split, watermark & password-protect documents.
- **Category**: Select "Tools" and "Productivity"
- **Base URL**: https://api.editpdfree.com

### Long Description
Copy the "Long Description" section from README.md in this directory.

### Tags
Add these tags (comma-separated):
```
pdf, html-to-pdf, url-to-pdf, pdf-converter, merge-pdf, compress-pdf, split-pdf, watermark, password-protect, pdf-manipulation, document-processing, html2pdf, web-to-pdf, pdf-generation, pdf-api, document-automation, pdf-tools
```

### Media
1. **Logo**: Upload a 400x400px logo
2. **Screenshots**: Add 3-5 screenshots showing:
   - API documentation
   - Example requests/responses
   - Use case examples
   - Dashboard/usage page
3. **Video** (optional): Demo video showing API in action

## Step 4: Configure Authentication

1. Select "API Key" authentication type
2. Configure:
   - **Key Name**: X-API-Key
   - **Key Location**: Header
   - **Key Prefix**: None (leave empty)

## Step 5: Set Up Pricing Plans

### Plan 1: Basic (Free)
- **Name**: Basic
- **Price**: $0.00/month
- **Quota**: 50 requests/month
- **Rate Limit**: 10 requests/minute
- **Description**: Perfect for testing and small projects
- **Features**:
  - All API endpoints
  - Standard support
  - Full documentation access

### Plan 2: Pro
- **Name**: Pro
- **Price**: $9.00/month
- **Quota**: 500 requests/month
- **Rate Limit**: 30 requests/minute
- **Description**: Ideal for small businesses and developers
- **Features**:
  - All API endpoints
  - Priority support
  - 99.9% uptime SLA
  - Usage analytics

### Plan 3: Ultra
- **Name**: Ultra
- **Price**: $24.00/month
- **Quota**: 5,000 requests/month
- **Rate Limit**: 60 requests/minute
- **Description**: Great for growing businesses
- **Features**:
  - All API endpoints
  - Priority support
  - 99.9% uptime SLA
  - Advanced usage analytics
  - Email alerts

### Plan 4: Mega
- **Name**: Mega
- **Price**: $49.00/month
- **Quota**: 20,000 requests/month
- **Rate Limit**: 120 requests/minute
- **Description**: Perfect for enterprise applications
- **Features**:
  - All API endpoints
  - Dedicated support
  - 99.9% uptime SLA
  - Advanced usage analytics
  - Email alerts
  - Custom branding options
  - Priority processing

## Step 6: Add Code Examples

RapidAPI will auto-generate code snippets, but you can customize them. Add these examples:

### Example 1: HTML to PDF (JavaScript)
```javascript
const axios = require('axios');

const options = {
  method: 'POST',
  url: 'https://api.editpdfree.com/api/v1/html-to-pdf',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_API_KEY'
  },
  data: {
    html: '<html><body><h1>Invoice</h1><p>Total: $99.99</p></body></html>',
    options: {
      format: 'A4',
      margin: { top: '1cm', right: '1cm', bottom: '1cm', left: '1cm' },
      footer_html: '<div style="text-align:center;font-size:10px;">Page {page} of {total}</div>'
    }
  },
  responseType: 'arraybuffer'
};

axios.request(options)
  .then(response => {
    // Save PDF file
    const fs = require('fs');
    fs.writeFileSync('output.pdf', response.data);
    console.log('PDF generated successfully!');
  })
  .catch(error => console.error(error));
```

### Example 2: URL to PDF (Python)
```python
import requests

url = "https://api.editpdfree.com/api/v1/url-to-pdf"

payload = {
    "url": "https://www.example.com",
    "options": {
        "format": "A4",
        "landscape": False,
        "print_background": True
    }
}

headers = {
    "Content-Type": "application/json",
    "X-API-Key": "YOUR_API_KEY"
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    with open("webpage.pdf", "wb") as f:
        f.write(response.content)
    print("PDF saved successfully!")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### Example 3: Merge PDFs (cURL)
```bash
curl -X POST "https://api.editpdfree.com/api/v1/merge" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf" \
  -F "files=@document3.pdf" \
  --output merged.pdf
```

### Example 4: Add Watermark (PHP)
```php
<?php
$curl = curl_init();

curl_setopt_array($curl, [
  CURLOPT_URL => "https://api.editpdfree.com/api/v1/watermark",
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_POST => true,
  CURLOPT_HTTPHEADER => [
    "X-API-Key: YOUR_API_KEY"
  ],
  CURLOPT_POSTFIELDS => [
    'file' => new CURLFile('document.pdf'),
    'text' => 'CONFIDENTIAL',
    'opacity' => 0.3,
    'position' => 'center',
    'font_size' => 60
  ]
]);

$response = curl_exec($curl);
$err = curl_error($curl);

curl_close($curl);

if ($err) {
  echo "Error: " . $err;
} else {
  file_put_contents('watermarked.pdf', $response);
  echo "Watermark added successfully!";
}
?>
```

## Step 7: Configure Endpoints

Review auto-imported endpoints from OpenAPI spec:

1. **POST /api/v1/html-to-pdf**
   - Add description and example request/response
   - Test the endpoint with sample data

2. **POST /api/v1/url-to-pdf**
   - Add description and example
   - Test with public URL

3. **POST /api/v1/merge**
   - Add description and example
   - Test with sample PDFs

4. **POST /api/v1/compress**
   - Add description for each quality level
   - Test compression results

5. **POST /api/v1/split**
   - Add page range syntax examples
   - Test page extraction

6. **POST /api/v1/watermark**
   - Add position and opacity examples
   - Test watermark rendering

7. **POST /api/v1/protect**
   - Add password security notes
   - Test encryption

8. **GET /api/v1/usage**
   - Add quota tracking explanation
   - Test usage response

## Step 8: Set Up Support & Documentation

### Support Channels
- **Email**: support@editpdfree.com
- **Response Time**:
  - Basic: 24 hours
  - Pro: 12 hours
  - Ultra: 8 hours
  - Mega: 4 hours

### Documentation Links
- **API Docs**: https://api.editpdfree.com/docs
- **Getting Started Guide**: Create a quick start guide
- **FAQ**: Add common questions and answers
- **Changelog**: Maintain version history

### FAQ Examples
```markdown
**Q: What file size limits apply?**
A: Maximum 50MB per request for all endpoints.

**Q: How is compression quality determined?**
A: Low (10-30% reduction), Medium (30-50%), High (50-70%).

**Q: Can I use custom fonts in HTML to PDF?**
A: Yes, use web fonts or base64-encoded fonts in your HTML.

**Q: Are there webhook notifications?**
A: Coming soon - async processing with webhooks.

**Q: What PDF version is generated?**
A: PDF 1.7 with full compatibility.

**Q: Do you store uploaded files?**
A: No, all files are processed in-memory and deleted immediately.
```

## Step 9: Testing Before Publishing

1. **Test All Endpoints**:
   - Use RapidAPI's built-in testing tool
   - Test with valid and invalid inputs
   - Verify error messages are clear

2. **Test Authentication**:
   - Generate test API keys
   - Verify rate limiting works
   - Test expired/invalid keys

3. **Test Quota System**:
   - Verify usage tracking
   - Test quota enforcement
   - Confirm reset timing

4. **Performance Testing**:
   - Test response times
   - Verify concurrent requests
   - Check large file handling

## Step 10: Submit for Review

1. Click "Submit for Review"
2. RapidAPI team will review (typically 2-5 business days)
3. Address any feedback or required changes
4. Once approved, your API will be live!

## Step 11: Post-Launch Optimization

### Monitor Performance
- Track API usage analytics
- Monitor error rates
- Review user feedback

### Marketing
- Share API on social media
- Write blog posts about use cases
- Create video tutorials
- Engage with developer community

### Optimization
- Add more code examples based on user requests
- Improve documentation clarity
- Optimize pricing based on usage patterns
- Add new endpoints based on demand

### Customer Support
- Respond to questions quickly
- Create knowledge base articles
- Share best practices
- Collect feature requests

## Additional Tips

### SEO Optimization
- Use relevant keywords in description
- Add comprehensive tags
- Include use case examples
- Keep documentation updated

### Conversion Optimization
- Highlight unique features
- Show competitive advantages
- Include customer testimonials (when available)
- Offer generous free tier

### Technical Best Practices
- Maintain 99.9% uptime
- Keep response times under 5 seconds
- Provide detailed error messages
- Version API properly (v1, v2, etc.)

### Revenue Optimization
- Monitor plan conversion rates
- A/B test pricing
- Offer annual discounts
- Consider custom enterprise plans

## Troubleshooting

### Common Issues

**Issue**: OpenAPI import fails
- **Solution**: Validate YAML syntax at https://editor.swagger.io
- Check server URL is correct
- Verify all required fields are present

**Issue**: Authentication not working
- **Solution**: Verify X-API-Key header name
- Check key is in header, not query params
- Test with valid API key

**Issue**: Rate limits not enforced
- **Solution**: Configure rate limits in plan settings
- Enable quota tracking in backend
- Test with high-volume requests

**Issue**: Low signup rate
- **Solution**: Improve API description
- Add more code examples
- Reduce free tier restrictions
- Highlight unique features

## Support

If you need help with the RapidAPI setup:
- RapidAPI Support: support@rapidapi.com
- RapidAPI Provider Docs: https://docs.rapidapi.com/docs/provider-quick-start
- EditPDFree Support: support@editpdfree.com

## Next Steps After Publishing

1. Monitor first users and gather feedback
2. Create tutorial blog posts
3. Engage in developer forums (Reddit, Stack Overflow)
4. Consider partnerships with complementary APIs
5. Plan feature roadmap based on user requests
6. Optimize pricing based on actual usage patterns

---

Good luck with your RapidAPI listing! The key to success is great documentation, responsive support, and continuous improvement based on user feedback.
