<link rel="stylesheet" href="styles/argumentation-tags.css">

# Argumentation Framework

This document defines the logical tags used throughout the repository to categorize different types of arguments and reasoning.

## Tag Types

### 📘 Descriptive

<a href="Argumentation.md#-descriptive" class="tag tag-descriptive"></a>

**Purpose:** Marks content that describes facts, situations, concepts, or current states of affairs without making normative claims.

**Characteristics:**
- Presents information about what *is* rather than what *ought to be*
- Documents observable phenomena, historical events, or accepted knowledge
- Provides context and background for arguments
- Does not assert moral judgments or prescriptive conclusions

**Example:** "Throughout history, societies have organized themselves into hierarchical structures with systems of governance and law."

---

### 📊 Empirical

<a href="Argumentation.md#-empirical" class="tag tag-empirical"></a>

**Purpose:** Indicates content based on scientific evidence, research findings, statistical data, or observable measurements.

**Characteristics:**
- References scientific studies, experiments, or data
- Cites measurable or testable phenomena
- Draws from peer-reviewed research or established scientific consensus
- Can be verified through observation or experimentation

**Example:** "Studies show that individuals who engage in regular physical exercise demonstrate improved cognitive function and reduced rates of depression."

---

### 📊 Illustrative Example

<a href="Argumentation.md#-illustrative-example" class="tag tag-illustrative"></a>

**Purpose:** Marks hypothetical scenarios, thought experiments, or specific examples used to clarify or demonstrate a concept.

**Characteristics:**
- Provides concrete instances to illustrate abstract principles
- May use hypothetical or real-world scenarios
- Helps readers understand implications of arguments
- Makes theoretical concepts more tangible

**Example:** "Imagine a society where resources are distributed based on merit rather than need, and consider how this might affect social cohesion."

---

### 🔗 Inference

<a href="Argumentation.md#-inference" class="tag tag-inference"></a>

**Purpose:** Marks logical conclusions drawn from premises, evidence, or previous arguments.

**Characteristics:**
- Represents the logical endpoint of a chain of reasoning
- Derives new claims from established premises or evidence
- Shows the result of applying logical operations to inputs
- Often uses words like "therefore," "thus," "it follows that," "we must conclude"

**Example:** "Therefore, if we accept that freedom requires the absence of coercion, and that laws necessarily involve coercion, it follows that absolute freedom is incompatible with any legal system."

---

### 🧠 Implicit Assumptions

<a href="Argumentation.md#-implicit-assumptions" class="tag tag-implicit"></a>

**Purpose:** Identifies unstated assumptions, hidden premises, or background beliefs that underlie an argument but are not explicitly stated.

**Characteristics:**
- Highlights assumptions that the argument depends on but doesn't explicitly state
- Points to cultural, philosophical, or contextual presuppositions
- May reveal potential weaknesses or areas for challenge in an argument
- Often represents commonly held beliefs that the author takes for granted

**Example:** An argument about justice might implicitly assume that humans have free will, or that equality of outcome is morally superior to equality of opportunity.

---

### ⚔️ Rebuttal

<a href="Argumentation.md#️-rebuttal" class="tag tag-rebuttal"></a>

**Purpose:** Marks counterarguments or objections that challenge a claim, premise, or line of reasoning.

**Characteristics:**
- Directly challenges or refutes a previous argument or claim
- Presents alternative interpretations or contradictory evidence
- Identifies flaws in reasoning or logical inconsistencies
- May introduce competing frameworks or perspectives
- Often uses phrases like "however," "but," "on the contrary," "this fails to account for"

**Example:** "However, this argument overlooks the fact that historical hierarchies were often maintained through force rather than merit, suggesting that their existence doesn't necessarily validate their moral legitimacy."

---

### ⚡ Important Premise Callout

In addition to the inline tags above, you can highlight particularly crucial premises using a special callout block. This is useful for foundational claims that are central to multiple arguments throughout the document.

**Usage:**
```html
<div class="important-premise">
<p>The outside observer is unable to externally define what would improve any specific individual person's subjective experience of reality.</p>
</div>
```

**Characteristics:**
- Visually distinct block-level element with prominent styling
- Used sparingly for the most critical foundational premises
- Draws reader attention to claims that underpin major arguments
- Should contain premises that, if questioned, would fundamentally alter the argument structure

---

### 💡 Important Conclusion Callout

Similar to the premise callout, you can highlight particularly significant conclusions using a special callout block. This is useful for emphasizing the key takeaways or final inferences from complex chains of reasoning.

**Usage:**
```html
<div class="important-conclusion">
<p>Therefore, any system of governance must balance individual liberty with collective welfare, recognizing that absolute freedom is neither achievable nor desirable in a functioning society.</p>
</div>
```

**Characteristics:**
- Visually distinct block-level element with purple-themed styling
- Used to emphasize major conclusions that result from extensive argumentation
- Draws reader attention to the ultimate inferences or synthesized positions
- Should contain conclusions that represent the culmination of significant reasoning
- Best placed at the end of major argument sections or at the document's conclusion

---

## Using These Tags

These tags help readers:
1. **Track the structure** of complex arguments
2. **Distinguish between** different types of claims
3. **Evaluate the strength** of reasoning by identifying which elements are empirical vs. assumed
4. **Follow the logical flow** from premises to conclusions

When reading a document with these tags, pay attention to:
- Whether empirical claims are properly supported
- Whether premises are reasonable or need questioning
- Whether inferences logically follow from their inputs
- Whether examples genuinely illustrate the points they claim to support
