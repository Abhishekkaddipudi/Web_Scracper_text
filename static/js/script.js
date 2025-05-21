    // Page navigation
    const pages = document.querySelectorAll('.page');
    let currentPage = 0;

    function showPage(index) {
  // make sure every page stays visible
  pages.forEach(page => page.classList.add('active'));

  // then scroll smoothly to the "current" one
  pages[index].scrollIntoView({ behavior: 'smooth' });
    }
    


    // Theme toggle logic
    const themeBtn = document.getElementById('theme-toggle');
    const savedTheme = localStorage.getItem('theme');
    const hamburger = document.getElementById('hamburger');
    const header = document.getElementById('header');
    const headerContent = document.getElementById('header-content');
    const body = document.body;

    // Set initial theme
    function setInitialTheme() {
      if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        themeBtn.textContent = '☀️';
      } else if (!savedTheme) {
        const hour = new Date().getHours();
        if (hour >= 6 && hour < 18) {
          document.body.classList.add('light-theme');
          themeBtn.textContent = '☀️';
        }
      }
    }
    setInitialTheme();

    themeBtn.addEventListener('click', () => {
      const isLight = document.body.classList.toggle('light-theme');
      localStorage.setItem('theme', isLight ? 'light' : 'dark');
      themeBtn.textContent = isLight ? '☀️' : '🌙';
    });
  let headerVisible=false
 hamburger.addEventListener('click', function () {
  this.classList.toggle('active');
  header.classList.toggle('header-visible');
  body.classList.toggle('body-pushed');

  if (!headerVisible) {
  const dataTag = document.getElementById("data");
  const { start, end,novel_title } = JSON.parse(dataTag.textContent);


    const currentStart = start || 1;
    const currentEnd = end || currentStart + 9;

    const headerTemplate = `
      <h1>${novel_title}</h1>
      <form id="range-form" method="POST">
        <label for="start">Start:</label>
        <input type="number" name="start" id="start" min="1" value="${currentStart}" required>
        <label for="end">End:</label>
        <input type="number" name="end" id="end" min="1" value="${currentEnd}" required>
        <div style="display: flex; gap: 10px; margin-top: 10px;">
          <button type="button" class="next-button">&lt;</button>
          <button type="button" class="previous-button">&gt;</button>
          <button type="submit">Load</button>
        </div>
      </form>
    `;

    headerContent.innerHTML = headerTemplate;
    headerVisible = true;

    const nextBtn = document.querySelector('.next-button');
    const prevBtn = document.querySelector('.previous-button');

    function adjustAndSubmit(delta) {
      const form = document.getElementById('range-form');
      const startInput = form.querySelector('input[name="start"]');
      const endInput = form.querySelector('input[name="end"]');

      let start = parseInt(startInput.value, 10) || 1;
      let end = parseInt(endInput.value, 10) || start;

      start += delta;
      end += delta;

      if (start < 1) start = 1;
      if (end < start) end = start;

      startInput.value = start;
      endInput.value = end;

      form.submit();
    }

    nextBtn.addEventListener('click', (e) => {
      e.preventDefault();
      adjustAndSubmit(-10); // "<" = go back 10 chapters
    });

    prevBtn.addEventListener('click', (e) => {
      e.preventDefault();
      adjustAndSubmit(10); // ">" = go forward 10 chapters
    });
  }
});
