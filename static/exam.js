const timer = document.querySelector('#timer');
const form = document.querySelector('#exam-form');
let seconds = Number(timer?.dataset.seconds || 0);
let submitted = false;
function renderTime() {
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  timer.querySelector('strong').textContent = `${String(minutes).padStart(2,'0')}:${String(remainder).padStart(2,'0')}`;
  if (seconds <= 60) timer.classList.add('urgent');
}
renderTime();
if (seconds <= 0) { submitted = true; form.submit(); }
else {
  const interval = setInterval(() => {
    seconds -= 1; renderTime();
    if (seconds <= 0) { clearInterval(interval); submitted = true; form.submit(); }
  }, 1000);
}
form.addEventListener('submit', event => {
  if (!submitted && !window.confirm('Submit your examination now? You cannot change your answers afterward.')) event.preventDefault();
  else submitted = true;
});
window.addEventListener('beforeunload', event => { if (!submitted) { event.preventDefault(); event.returnValue=''; } });
