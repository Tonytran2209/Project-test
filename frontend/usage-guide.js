(() => {
  const trigger = document.getElementById("usageGuideButton");
  const dialog = document.getElementById("usageGuideDialog");
  const closeButton = document.getElementById("usageGuideCloseButton");
  const previousButton = document.getElementById("usageGuidePreviousButton");
  const nextButton = document.getElementById("usageGuideNextButton");
  const stepLabel = document.getElementById("usageGuideStepLabel");
  const title = document.getElementById("usageGuideTitle");
  const description = document.getElementById("usageGuideDescription");
  const preview = dialog?.querySelector(".usage-guide-preview");
  const acceptancePreview = document.getElementById("usageGuideAcceptancePreview");
  const messagesPreview = document.getElementById("usageGuideMessagesPreview");
  const repliesPreview = document.getElementById("usageGuideRepliesPreview");
  if (!trigger || !dialog || !closeButton || !previousButton || !nextButton || !stepLabel || !title || !description || !preview || !acceptancePreview || !messagesPreview || !repliesPreview) return;

  const steps = [
    { name: "Connect", title: "No more manual Connect clicks", description: "BD used to open each LinkedIn profile and click Connect by hand. Now you provide the profile URLs, and the worker sends the invitations for you. This step removes that repetitive manual work from the outreach process." },
    { name: "Acceptance", title: "See who accepted your invitations", description: "The worker rechecks Connect batches automatically on its configured schedule. Acceptance keeps results on the original Connect batch. You can still select a week and check an individual job manually." },
    { name: "Messages", title: "Send automatically prepared messages", description: "Acceptance automatically prepares new accepted recipients using the saved campaign template. Open Ready in Messages and confirm Queue & Send. Needs info keeps recipients missing required data. Queued, Sending, Completed and Failed track progress. No manual Prepare step is needed, and no messages are sent automatically." },
    { name: "Replies", title: "Manage replies from one inbox", description: "The reply-check worker scans Unread for every Outreach account twice a day, at 12:00 and 18:00 Vietnam time—not in real time. It matches senders with profiles we messaged, reads their conversation histories, and syncs them into Replies after each scan. Choose the account and conversation, write your response, then confirm Send via worker to reply from that account to the matching LinkedIn profile." },
  ];
  let activeStep = 0;

  function showStep(index) {
    activeStep = index;
    const step = steps[index];
    stepLabel.textContent = `STEP ${String(index + 1).padStart(2, "0")} OF ${String(steps.length).padStart(2, "0")}`;
    title.textContent = step.title || step.name;
    description.textContent = step.description || `The ${step.name} guide is being prepared.`;
    preview.hidden = index !== 0;
    acceptancePreview.hidden = index !== 1;
    messagesPreview.hidden = index !== 2;
    repliesPreview.hidden = index !== 3;
    previousButton.disabled = index === 0;
    nextButton.disabled = index === steps.length - 1;

    dialog.classList.remove("is-playing");
    // Restart the illustration whenever a guide step appears.
    void dialog.offsetWidth;
    dialog.classList.add("is-playing");
  }

  trigger.addEventListener("click", () => {
    if (dialog.open) return;
    dialog.showModal();
    showStep(0);
    closeButton.focus();
  });

  const close = () => dialog.close();
  closeButton.addEventListener("click", close);
  previousButton.addEventListener("click", () => {
    if (activeStep > 0) showStep(activeStep - 1);
  });
  nextButton.addEventListener("click", () => {
    if (activeStep < steps.length - 1) showStep(activeStep + 1);
  });
  dialog.addEventListener("close", () => {
    dialog.classList.remove("is-playing");
    trigger.focus();
  });
  dialog.addEventListener("click", (event) => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) close();
  });
})();
