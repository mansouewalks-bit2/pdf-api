# Reddit Marketing Posts for PDF API

## 1. r/webdev

**Title:** I built a free PDF API for developers (html-to-pdf, url-to-pdf, merge, etc.)

**Body:**

Hey everyone,

I've been working on a side project for the past few months and finally launched it: a PDF processing API that I actually wanted to use myself.

The problem I kept running into was needing to generate PDFs from HTML or merge documents, and all the existing solutions were either expensive, had terrible docs, or required installing a bunch of dependencies locally.

So I built https://api.editpdfree.com - it's a REST API for:
- HTML to PDF (with full CSS support)
- URL to PDF (screenshot any webpage)
- Merge/split/compress PDFs
- Add watermarks
- Password protection

It uses Chromium under the hood via Playwright, so the rendering is pixel-perfect. No wkhtmltopdf weirdness.

**Quick example:**

```bash
curl -X POST https://api.editpdfree.com/html-to-pdf \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"html": "<h1>Hello World</h1>"}' \
  --output output.pdf
```

Free tier is 50 conversions/month, no credit card needed. I wanted to make it easy for hobby projects and testing.

Built with FastAPI + Playwright + Docker. Happy to answer any questions about the stack or implementation!

**Best time to post:** Tuesday or Wednesday, 9-11 AM EST (when US devs are active)

**Engagement tips:**
- Reply quickly to technical questions
- Share code snippets if people ask about implementation
- Don't be defensive if people compare to alternatives
- Offer to help with integration issues
- If someone asks "why not use X", explain your use case honestly

---

## 2. r/SaaS

**Title:** Launched my first micro-SaaS: PDF API ($0 → $49 MRR in 2 weeks)

**Body:**

Hey r/SaaS,

I finally pulled the trigger and launched my first micro-SaaS after lurking here for months: a PDF processing API.

**The backstory:**

I run a free PDF tool website (editpdfree.com) that gets decent traffic, and I kept getting emails from developers asking if I had an API. I ignored them for a while, but after the 20th email I thought "maybe there's something here."

**What I built:**

A REST API for PDF operations: html-to-pdf, url-to-pdf, merge, compress, split, watermark, etc.

Stack: FastAPI + Playwright + Chromium (Docker deployed)

**Pricing:**
- Free: 50 conversions/month
- Starter: $9/month
- Pro: $24/month
- Business: $49/month

**Early results (2 weeks in):**
- 47 signups
- 3 paid customers ($49 MRR)
- $0 in marketing spend (just posted in a few Discord servers and on my existing site)

**What surprised me:**
1. People actually want the free tier - I thought it'd just attract tire-kickers, but some are converting after testing
2. Documentation matters MORE than features - I spent 2 days just writing examples
3. Stripe integration was easier than I thought
4. Rate limiting is harder than I thought (had to build my own middleware)

**What's next:**
- Add webhooks for async processing
- Build a Node.js SDK
- Maybe a WordPress plugin?

Link if you want to check it out: https://api.editpdfree.com

Happy to answer any questions about the build, pricing strategy, or tech stack!

**Best time to post:** Monday or Thursday, 10 AM - 2 PM EST

**Engagement tips:**
- Share actual revenue numbers (people love transparency)
- Talk about failures/mistakes, not just wins
- Answer questions about pricing strategy honestly
- If someone asks about competitors, acknowledge them and explain your differentiation
- Update the post with new MRR milestones in comments

---

## 3. r/sideproject

**Title:** My weekend project: A PDF API that actually works

**Body:**

I spent the last few weekends building something I've wanted for years: a simple PDF API that doesn't suck.

**The problem:**

Every time I needed to generate PDFs in my projects, I had two options:
1. Install some janky library that breaks on every OS update
2. Pay $50/month for an enterprise solution that's overkill

So I built option 3: https://api.editpdfree.com

**Features:**
- Convert HTML to PDF (full CSS/JS support)
- Convert any URL to PDF
- Merge, split, compress PDFs
- Add watermarks
- Password protection

**Tech stack:**
- Backend: FastAPI (Python)
- PDF engine: Playwright + Chromium
- Deployment: Docker on a VPS
- Auth: JWT tokens
- Rate limiting: Custom middleware with Redis

**What I learned:**
- Chromium rendering is 10x better than wkhtmltopdf
- Rate limiting is essential (someone tried to generate 10,000 PDFs on day 1)
- Stripe webhooks are actually pretty straightforward
- People REALLY care about good docs

Free tier is 50 conversions/month if anyone wants to try it. I'm using it for my own projects and figured others might find it useful.

Feedback welcome!

**Best time to post:** Saturday or Sunday, 2-6 PM EST (when people browse side projects)

**Engagement tips:**
- Share technical details when asked
- Post screenshots of the landing page or dashboard
- Be humble about the project ("still improving X")
- Ask for feedback on specific features
- Engage with other side projects in the comments

---

## 4. r/programming

**Title:** Building a PDF generation API with FastAPI and Playwright: Architecture and lessons learned

**Body:**

I recently built a PDF processing API and wanted to share some technical insights for anyone considering a similar project.

**The challenge:**

Most PDF generation libraries (wkhtmltopdf, ReportLab, etc.) have limitations:
- wkhtmltopdf: outdated WebKit, poor CSS support
- ReportLab: programmatic only, no HTML rendering
- Puppeteer/Playwright: good rendering, but tricky to scale

**My solution:**

I went with Playwright + Chromium for rendering, wrapped in a FastAPI service. Here's the architecture:

**Core components:**

1. **FastAPI backend** - async endpoints, automatic OpenAPI docs
2. **Playwright** - headless Chromium for PDF rendering
3. **Docker** - consistent environment across deployments
4. **Redis** - rate limiting and job queuing
5. **PostgreSQL** - user auth, usage tracking, API keys

**Key implementation details:**

```python
# Simplified PDF generation
async def html_to_pdf(html: str, options: dict):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html)
        pdf_bytes = await page.pdf(**options)
        await browser.close()
        return pdf_bytes
```

**Challenges solved:**

1. **Browser pooling**: Launching browsers is expensive (~2-3s). I maintain a pool of warm browsers to reduce latency.

2. **Memory leaks**: Chromium can leak if not properly closed. I use context managers and timeout enforcement.

3. **Security**: User-provided HTML can be dangerous. I run Chromium in a sandboxed Docker container with no network access.

4. **Rate limiting**: Built custom middleware to track requests per API key per time window.

**Performance:**
- Cold start: ~3s per PDF
- Warm start: ~500ms per PDF
- Can handle ~50 concurrent requests per instance

**Deployment:**
- Dockerized, runs on a VPS
- Nginx reverse proxy
- Let's Encrypt for SSL

**What I'd do differently:**
- Use Kubernetes instead of Docker Compose (struggling with scaling)
- Add a proper job queue (considering Celery + RabbitMQ)
- Implement caching for frequently generated PDFs

Live at https://api.editpdfree.com if anyone wants to check it out. Free tier available for testing.

Happy to answer technical questions!

**Best time to post:** Tuesday or Wednesday, 8-10 AM EST or 2-4 PM EST

**Engagement tips:**
- Focus on technical depth, not marketing
- Share actual code snippets
- Discuss trade-offs and alternatives openly
- Engage with technical critiques constructively
- Link to GitHub if you open-source any components
- Be prepared to discuss security, scaling, and architecture

---

## 5. r/Entrepreneur

**Title:** Building passive income with API products: My first $50 MRR

**Body:**

I've been following this sub for a while and wanted to share my first small win: I built a PDF API and hit $50 MRR after 2 weeks.

**Background:**

I'm a developer, not a marketer. I run a free PDF tool website (editpdfree.com) as a side project, and I kept getting emails from developers asking "do you have an API?"

After ignoring these for months, I finally realized: people are literally asking to pay me. Maybe I should listen.

**What I built:**

A REST API for PDF processing: convert HTML to PDF, URL to PDF, merge/split/compress files, add watermarks, etc.

**Why an API product?**

1. **Low maintenance**: Once it's running, it's mostly automated
2. **Recurring revenue**: Monthly subscriptions, not one-time payments
3. **Developer audience**: They know how to use it, less hand-holding
4. **Scalable**: Same code serves 1 customer or 100

**The numbers (2 weeks in):**
- 47 signups (mostly free tier)
- 3 paid customers
- $49 MRR ($9 + $24 + $16 prorated)
- ~$15/month in server costs
- $0 in marketing spend

**What worked:**
- Adding a generous free tier (50 requests/month)
- Posting in developer communities (Discord, Reddit)
- Making the docs REALLY good (spent 2 days on this)
- Using my existing website to cross-promote

**What didn't work:**
- Cold emails (0% response rate)
- Ads (tried $50 on Google Ads, got 0 conversions)

**Next steps:**
- Get to $200 MRR by end of month (realistic?)
- Build a WordPress plugin to reach non-developers
- Maybe launch a second API (QR codes or screenshot API)

The site: https://api.editpdfree.com

Anyone else building API products? I'd love to hear your experiences.

**Best time to post:** Monday, Wednesday, or Friday, 9 AM - 12 PM EST

**Engagement tips:**
- Share actual revenue numbers (entrepreneurs love data)
- Be honest about what didn't work
- Ask questions to engage the community
- Update with progress in the comments
- Don't oversell - stay humble and learning-focused
- Respond to DMs offering help/advice

---

## 6. r/startups

**Title:** Launched a PDF API - What I learned in the first 2 weeks

**Body:**

Two weeks ago I launched a PDF processing API. It's my first real product launch, and I wanted to share what I learned.

**The product:**

API for PDF operations: html-to-pdf, url-to-pdf, merge, compress, split, watermark, protect.

Website: https://api.editpdfree.com

**Validation before building:**

I actually didn't do much. I had a free PDF tool website getting traffic, and developers kept emailing asking for an API. After 20+ emails, I built it.

**Tech choices:**
- FastAPI (Python) - fast to build, great docs
- Playwright + Chromium - best rendering quality
- Deployed on a VPS - keeping costs low

**Pricing:**
- Free: 50 conversions/month
- Starter: $9/month
- Pro: $24/month
- Business: $49/month

**Results (2 weeks):**
- 47 signups
- 3 paid customers ($49 MRR)
- $0 marketing spend

**Key lessons:**

1. **Documentation > Features**: I spent 2 days just writing docs with code examples. Best time investment.

2. **Free tier = growth**: 90% of signups are free, but 2 of my 3 paid customers started on free tier.

3. **Developers want simplicity**: No login to test, no credit card for free tier, clear pricing.

4. **Rate limiting is crucial**: Someone tried to abuse the free tier on day 1. Built rate limiting that night.

5. **Stripe integration is easier than expected**: Took 3 hours to integrate subscriptions + webhooks.

6. **Launch everywhere at once**: I posted on Reddit, HackerNews, ProductHunt, and Discord servers on the same day. Got momentum.

**What I'm worried about:**

- Scaling (currently on one VPS)
- Customer support (I'm the only person)
- Churn (too early to tell)

**What's next:**

- Build SDKs (JavaScript, Python, PHP)
- Add webhooks for async processing
- Marketing (I suck at this)

Happy to answer questions about tech stack, pricing, or anything else!

**Best time to post:** Tuesday or Thursday, 10 AM - 1 PM EST

**Engagement tips:**
- Focus on lessons learned, not just promotion
- Be vulnerable about challenges and concerns
- Ask for advice on specific problems
- Engage with comments offering help
- Share metrics updates in comments
- Connect with other founders in the thread

---

## 7. r/IndieHackers Style (cross-post to Twitter/IndieHackers.com)

**Title:** $0 → $50 MRR in 2 weeks with a PDF API (technical breakdown)

**Body:**

I launched a PDF API 2 weeks ago and hit my first $50 in monthly recurring revenue. Here's the full breakdown.

**What I built:**

API for PDF processing: https://api.editpdfree.com

- HTML to PDF (Chromium rendering)
- URL to PDF (screenshot any page)
- Merge/split/compress PDFs
- Watermarks & password protection

**Stack:**
- FastAPI + Playwright + Chromium
- Docker deployment on VPS
- PostgreSQL + Redis
- Stripe for payments

**Time to build:** 6 weekends (~60 hours)

**Costs:**
- VPS: $15/month
- Domain: $12/year
- Stripe fees: ~3%
- **Total monthly: ~$17**

**Launch strategy:**
1. Posted on my existing website (editpdfree.com - gets ~2k visitors/day)
2. Posted in r/webdev, r/sideproject, r/programming
3. Shared in 5 Discord developer communities
4. Submitted to ProductHunt (tanked - 12 upvotes)

**Results (14 days):**
- 47 signups
- 3 paid customers
- $49 MRR ($9 + $24 + $16)
- $0 in ads

**Revenue by plan:**
- Free tier: 44 users
- Starter ($9): 2 users
- Pro ($24): 1 user
- Business ($49): 0 users

**What worked:**
- Generous free tier (50 requests/month)
- Great documentation with curl examples
- No credit card for free tier
- Fast support (I reply within 1 hour)

**What didn't work:**
- ProductHunt (wrong audience?)
- Google Ads ($50 spent, 0 conversions)
- Cold outreach (0% reply rate)

**Key metrics I'm tracking:**
- MRR growth week-over-week
- Free → Paid conversion rate (currently 6.4%)
- Churn rate (too early to measure)
- Average requests per user
- Support ticket volume

**Next 30 days:**
- Goal: $200 MRR
- Ship: JavaScript SDK
- Ship: Webhooks for async jobs
- Maybe: WordPress plugin

**Tech decisions I'm happy with:**
- FastAPI: Super fast to build APIs
- Playwright: Best PDF rendering I've used
- Stripe: Subscriptions were easier than expected

**Tech decisions I regret:**
- Manual VPS deployment (should've used Railway or Render)
- Not building a job queue from day 1 (scaling is hard now)

**Biggest lesson:**

Talk to users BEFORE building. I built features nobody asked for (compress PDF) while users actually wanted webhooks and SDKs.

**Open questions:**
- How do I scale past $1k MRR without paid ads?
- Should I build more API products or focus on this one?
- When do I need to incorporate (I'm just a solo dev with Stripe)?

Happy to answer questions!

**Best time to post:** Monday morning or Friday afternoon, 9 AM - 11 AM EST

**Engagement tips:**
- Share granular metrics (indie hackers love data)
- Be transparent about failures
- Post regular updates in comments ("Week 3 update: hit $80 MRR")
- Ask specific questions to drive engagement
- Connect with other indie hackers building similar products
- Share your roadmap and ask for feedback
- Consider posting monthly revenue updates as a series

---

## General Tips for All Posts

### DO:
- Post during US work hours (most Reddit users are US-based)
- Reply to every comment in the first 2 hours
- Be helpful, not salesy
- Share actual code/metrics when asked
- Upvote and engage with other posts before posting yours
- Use a throwaway account or your regular account (both work, just be consistent)
- Follow up in comments with updates

### DON'T:
- Spam the link multiple times in comments
- Argue with critics (acknowledge and move on)
- Post the same content to multiple subreddits on the same day (space them out)
- Use affiliate links or referral codes
- Delete your post if it doesn't get traction immediately
- Ignore negative feedback (address it constructively)

### Posting Schedule:
- Week 1: r/sideproject (Saturday)
- Week 1: r/webdev (Tuesday)
- Week 2: r/SaaS (Thursday)
- Week 2: r/Entrepreneur (Monday)
- Week 3: r/programming (Wednesday - most technical)
- Week 3: r/startups (Friday)
- Week 4: IndieHackers + Twitter thread

### Measurement:
- Track traffic from each post (UTM parameters: ?utm_source=reddit&utm_medium=r_webdev)
- Monitor signups by source
- Track which posts drove paid conversions
- Note which communities engage the most for future posts

---

## Follow-up Strategy

If a post gets traction (50+ upvotes), consider:

1. **Update with metrics**: "Edit: Thanks for the response! Got 200 signups from this thread, 5 paid customers"
2. **Answer common questions in the post**: Add an FAQ section
3. **Engage with critics**: "Good point about X, here's why I did Y"
4. **Offer discounts**: "Since this is getting traction, 50% off first month with code REDDIT50"
5. **Share learnings**: Post a follow-up 30 days later with results

Good luck!
