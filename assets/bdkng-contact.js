'use strict';
(() => {
  const form = document.getElementById('contact-form');
  if (!form) return;
  const topic = form.elements.namedItem('thema');
  const queryTopic = new URLSearchParams(window.location.search).get('thema');
  if ([...topic.options].some(option => option.value === queryTopic)) {
    topic.value = queryTopic;
  }
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const value = name => String(form.elements.namedItem(name).value).trim();
    const subject = 'BDKNG · ' + topic.options[topic.selectedIndex].text;
    const body = [
      'Thema: ' + topic.options[topic.selectedIndex].text,
      'Name: ' + (value('name') || 'Nicht angegeben'),
      'E-Mail: ' + value('email'),
      'Unternehmen / Verein: ' + (value('organisation') || 'Nicht angegeben'),
      '', value('nachricht'), '', 'Anfrage über https://bdkng.de/kontakt.html'
    ].join('\r\n');
    const link = document.getElementById('mail-draft');
    link.href = 'mailto:info@bdkng.de?subject=' + encodeURIComponent(subject)
      + '&body=' + encodeURIComponent(body);
    document.getElementById('mail-result').hidden = false;
    link.click();
  });
})();
