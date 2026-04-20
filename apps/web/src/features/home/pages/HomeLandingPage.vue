<template>
  <div class="home-page">
    <LegacyPublicHeader :transparent="!hasScrolled" />

    <section class="hero">
      <div class="hero__copy">
        <p class="hero__eyebrow">把零散想法拼成知識磚塊</p>
        <h1>讓會議、專案與重點整理回到舊版熟悉的樣子</h1>
        <p class="hero__description">
          以 BRICKS 的經典介面整理會議紀錄、搜尋脈絡與管理專案，同時保留新版前後端分層架構。
        </p>
        <div class="hero__actions">
          <RouterLink class="hero__button hero__button--primary" to="/register">立即開始</RouterLink>
          <RouterLink class="hero__button" to="/login">登入工作區</RouterLink>
        </div>
      </div>
    </section>

    <section class="feature feature--tight">
      <article class="feature__card">
        <img :src="screenShotUrl" alt="Bricks dashboard preview" />
        <div class="feature__text">
          <p class="feature__tag"># 專案總覽</p>
          <h2>把熟悉的卡片分組與專案欄位帶回來</h2>
          <p>
            依分類整理專案、快速搜尋名稱，保留舊版層級感與留白比例，操作節奏更接近原始 frontend。
          </p>
        </div>
      </article>

      <article class="feature__card feature__card--reverse">
        <img :src="screenShotUrl" alt="Bricks record preview" />
        <div class="feature__text">
          <p class="feature__tag"># 會議紀錄</p>
          <h2>用舊版的導覽與資訊面板查看紀錄內容</h2>
          <p>
            左側列表、上方工具列、右側內容面板都沿用經典視覺語言，但資料仍由新版 API 與 store 管理。
          </p>
        </div>
      </article>

      <article class="feature__closing">
        <h2>同一套使用習慣，新一代程式架構</h2>
        <p>
          這次改版把畫面還原到熟悉的 frontend 風格，同時保留新版可維護的 feature-based 結構，之後再擴充也更穩定。
        </p>
        <RouterLink class="hero__button hero__button--primary" to="/register">建立帳號</RouterLink>
      </article>
    </section>

    <LegacyPublicFooter />
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";

import screenShotUrl from "@/assets/legacy/screen_shot.png";
import LegacyPublicFooter from "@/shared/ui/legacy/LegacyPublicFooter.vue";
import LegacyPublicHeader from "@/shared/ui/legacy/LegacyPublicHeader.vue";

const hasScrolled = ref(false);

function handleScroll() {
  hasScrolled.value = window.scrollY > window.innerHeight * 0.65;
}

onMounted(() => {
  handleScroll();
  window.addEventListener("scroll", handleScroll, { passive: true });
});

onBeforeUnmount(() => {
  window.removeEventListener("scroll", handleScroll);
});
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background:
    url("@/assets/legacy/bricks_bg.svg") center top / cover no-repeat,
    #fff;
}

.hero {
  min-height: 100vh;
  padding: 8rem 5.21% 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: url("@/assets/legacy/homepage_bg.svg") center center / cover no-repeat;
}

.hero__copy {
  width: min(40rem, 100%);
  text-align: center;
}

.hero__eyebrow {
  margin: 0 0 1rem;
  font-size: clamp(1rem, 2vw, 1.3rem);
  letter-spacing: 0.35em;
}

.hero h1 {
  margin: 0;
  font-size: clamp(2.8rem, 7vw, 5.2rem);
  line-height: 1.06;
  letter-spacing: 0.12em;
}

.hero__description {
  margin: 1.75rem auto 0;
  width: min(34rem, 100%);
  font-size: clamp(1rem, 2vw, 1.35rem);
  line-height: 1.75;
}

.hero__actions {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.hero__button {
  min-width: 12rem;
  border: 1px solid #b82c30;
  border-radius: 14px;
  padding: 0.9rem 1.4rem;
  text-align: center;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.88);
  color: #b82c30;
}

.hero__button:hover {
  background: #f2eeee;
}

.hero__button--primary {
  background: #b82c30;
  color: #fff;
}

.hero__button--primary:hover {
  background: #d48083;
}

.feature {
  padding: 5rem 5.21%;
  display: grid;
  gap: 3rem;
}

.feature__card {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  gap: 3rem;
  align-items: center;
}

.feature__card--reverse {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr);
}

.feature__card--reverse img {
  order: 2;
}

.feature__card img {
  width: 100%;
  border-radius: 20px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
}

.feature__tag {
  margin: 0 0 0.75rem;
  color: #b6aeae;
  font-weight: 700;
}

.feature__text h2,
.feature__closing h2 {
  margin: 0;
  font-size: clamp(2rem, 3.4vw, 3.2rem);
  line-height: 1.2;
}

.feature__text p,
.feature__closing p {
  margin: 1rem 0 0;
  font-size: 1.05rem;
  line-height: 1.9;
}

.feature__closing {
  width: min(46rem, 100%);
  margin: 0 auto;
  text-align: center;
}

.feature__closing .hero__button {
  margin-top: 2rem;
}

@media (max-width: 980px) {
  .feature__card,
  .feature__card--reverse {
    grid-template-columns: 1fr;
  }

  .feature__card--reverse img {
    order: 0;
  }
}

@media (max-width: 720px) {
  .hero {
    padding-top: 10rem;
  }
}
</style>
