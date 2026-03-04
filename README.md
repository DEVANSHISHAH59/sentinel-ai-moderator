A small prototype moderation system that analyses text and estimates content risk levels.

The goal of this project is to simulate a simplified Trust & Safety workflow used by large online platforms.

Instead of manually reviewing every piece of content, moderation teams need tools that can:

detect potentially harmful content

prioritise high-risk items

track moderation trends

This project demonstrates how such a system might work.

Problem

Online platforms receive large volumes of user-generated content.

Moderation teams need tools that help them quickly answer questions like:

Which content should be reviewed first?

What types of violations are most common?

How risky is the overall content stream?

This prototype explores how machine learning can support those decisions.

What the app does

The dashboard allows users to:

• analyse text content for potential policy violations
• estimate a risk score for each piece of content
• simulate moderation decisions
• view analytics about flagged content

Example moderation outputs

The system classifies content into different risk categories.

Possible outcomes:

Allow
Content appears safe.

Review
Content should be reviewed by a moderator.

Remove
Content likely violates platform policy.

Dashboard analytics

The dashboard visualises moderation trends including:

percentage of flagged content

risk score distribution

policy category breakdown

common flagged terms

Technology

Python
Streamlit
Machine learning classifiers
Text processing

Live Demo

https://sentinel-ai-moderator-dqtmurpww6ta8kcrgs6kat.streamlit.app/
Future Improvements

larger moderation dataset

improved policy classification

batch content analysis

model evaluation metrics
