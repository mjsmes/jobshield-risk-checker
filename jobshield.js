(() => {
  const textarea = document.querySelector("#job-text");
  const counter = document.querySelector("#char-count");
  const sampleButton = document.querySelector("#sample-button");

  if (!(textarea instanceof HTMLTextAreaElement)) return;

  const maximum = Number(textarea.maxLength);
  const updateCounter = () => {
    if (counter) {
      counter.textContent = `${textarea.value.length.toLocaleString()} / ${maximum.toLocaleString()}`;
    }
  };

  textarea.addEventListener("input", updateCounter);

  if (sampleButton instanceof HTMLButtonElement) {
    sampleButton.addEventListener("click", () => {
      textarea.value =
        "Congratulations! You have been selected for our remote assistant role. " +
        "Earn KSh 80,000 every week with no experience. Pay a KSh 1,500 " +
        "registration fee today to reserve your position. Act now—only two " +
        "slots remain. Send your PIN and OTP to our recruiter on WhatsApp.";
      updateCounter();
      textarea.focus();
    });
  }
})();
