# Email Signature Templates

---

## Default Signature (Plain Text)

Automatically added to all outgoing emails:

```
---
Sent with Claude Code
```

---

## Default Signature (HTML)

```html
<hr style="margin-top: 20px; border: none; border-top: 1px solid #ddd;">
<p style="color: #888; font-size: 12px;">Sent with Claude Code</p>
```

---

## Business Signature (Plain Text)

```
---
{Name}
{Title} | {Company}
{Email} | {Phone}

Sent with Claude Code
```

---

## Business Signature (HTML)

```html
<hr style="margin-top: 20px; border: none; border-top: 1px solid #ddd;">
<table style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
  <tr>
    <td style="padding-right: 15px; border-right: 2px solid #0066cc;">
      <!-- If logo image available -->
      <!-- <img src="logo.png" width="60" alt="Company Logo"> -->
    </td>
    <td style="padding-left: 15px;">
      <strong style="font-size: 16px; color: #0066cc;">{Name}</strong><br>
      <span style="color: #666;">{Title} | {Company}</span><br>
      <span style="font-size: 12px;">
        📧 {Email}<br>
        📱 {Phone}
      </span>
    </td>
  </tr>
</table>
<p style="color: #aaa; font-size: 11px; margin-top: 10px;">Sent with Claude Code</p>
```

---

## Minimal Signature

```
--
{Name}
```

---

## Signature Usage Guide

1. **Default signature**: `Sent with Claude Code` is automatically added to all emails
2. **Business signature**: Use for external partners and customer emails
3. **Minimal signature**: Use for quick communication between internal team members
4. **HTML signature**: Applied when using `--html` flag
