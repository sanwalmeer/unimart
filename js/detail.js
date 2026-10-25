const contactButton = document.getElementById('contactSellerButton');

const openContactPrompt = () => {
  const next = `${window.location.pathname}${window.location.search}`;
  const encodedNext = encodeURIComponent(next);
  const modal = document.createElement('div');
  modal.className = 'contact-modal-backdrop';
  modal.setAttribute('role', 'presentation');
  modal.innerHTML = `
    <section class="contact-modal" role="dialog" aria-modal="true" aria-labelledby="contactPromptTitle">
      <button class="contact-modal-close" type="button" aria-label="Close">×</button>
      <p class="eyebrow">A safer campus marketplace</p>
      <h2 id="contactPromptTitle">Connect with the seller</h2>
      <p>Log in or create a free UniMart account to continue. Seller contact details are never shown publicly.</p>
      <div class="contact-modal-actions">
        <a class="primary-button" href="/?auth=signup&amp;next=${encodedNext}">Sign up</a>
        <a class="secondary-button" href="/?auth=login&amp;next=${encodedNext}">Log in</a>
      </div>
    </section>`;
  document.body.append(modal);
  const close = () => modal.remove();
  modal.querySelector('.contact-modal-close').addEventListener('click', close);
  modal.addEventListener('click', (event) => {
    if (event.target === modal) close();
  });
  modal.querySelector('.contact-modal-close').focus();
};

contactButton?.addEventListener('click', openContactPrompt);
