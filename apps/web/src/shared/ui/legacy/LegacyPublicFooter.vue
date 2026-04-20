<template>
  <footer class="public-footer">
    <a class="public-footer__link" href="#">隱私權政策</a>
    <a class="public-footer__link" href="#">聯絡我們 bricks@gmail.com</a>
    <p class="public-footer__credit">
      Photo by
      <a href="https://unsplash.com/@charlesdeluvio" target="_blank" rel="noreferrer">charlesdeluvio</a>
      on Unsplash
    </p>
  </footer>
</template>

<style scoped>
.public-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 1.25rem 2rem;
  min-height: 64px;
  padding: 1rem 5.21%;
  background: #fff;
  box-shadow: 0 -4px 8px rgba(0, 0, 0, 0.08);
  color: #120406;
}

.public-footer__link,
.public-footer__credit {
  margin: 0;
  font-size: 0.95rem;
  color: #120406;
  text-decoration: none;
}

.public-footer__link:hover {
  text-decoration: underline;
}

.public-footer__credit,
.public-footer__credit a {
  color: #b6aeae;
}

@media (max-width: 820px) {
  .public-footer {
    justify-content: flex-start;
  }
}
</style>
