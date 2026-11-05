"use strict";
const copyButton = document.getElementById("copy-hash");
copyButton.addEventListener("click", async () => {
  const hash = document.getElementById("hash").textContent.trim();
  const status = document.getElementById("copy-status");
  try {
    await navigator.clipboard.writeText(hash);
    status.textContent = "已复制完整校验值";
    copyButton.textContent = "已复制 ✓";
    window.setTimeout(() => { copyButton.textContent = "复制校验值"; }, 2500);
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(document.getElementById("hash"));
    selection.removeAllRanges();
    selection.addRange(range);
    status.textContent = "已选中校验值，请按 Ctrl+C 复制";
  }
});
