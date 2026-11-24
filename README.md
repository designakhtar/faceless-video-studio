# Faceless Video Studio

## ব্যবহার
Claude Code-এ এই ফোল্ডার খুলে লিখুন: `/faceless-video <বিষয়>` অথবা "ফেসলেস ভিডিও চালু করো: ..."।

Claude চার জায়গায় থেমে আপনার OK নেবে: স্ক্রিপ্ট, খরচ, টেস্ট শট, ফাইনাল।

## আগে যা লাগবে
1. Chrome খোলা, Claude in Chrome এক্সটেনশনে এই অ্যাপের অ্যাকাউন্টে সাইন ইন।
2. ওই Chrome-এ Google Flow-এ লগইন (Google AI Pro)।
3. কণ্ঠের জন্য Higgsfield ক্রেডিট, অথবা নিজের রেকর্ডিং।

## খরচ
Flow (শট) আর Higgsfield (কণ্ঠ) ক্রেডিট খরচ করে। স্ক্রিপ্ট আপনার Claude প্ল্যানে। মিউজিক, ক্যাপশন, কার্ড, এডিটিং ফ্রি।

## নতুন কম্পিউটারে
Node.js, Python আর FFmpeg বসিয়ে `npm install` চালান, তারপর `py tools/studio.py check`।

## ফোল্ডার
`scripts` স্ক্রিপ্ট, `storyboards` শট তালিকা, `characters` চরিত্র, `shots` ক্লিপ, `graphics` কার্ড, `audio` কণ্ঠ ও মিউজিক,
`final` ফাইনাল ভিডিও ও রিপোর্ট, `tools` টুল, `.claude/skills/faceless-video` স্কিল।
