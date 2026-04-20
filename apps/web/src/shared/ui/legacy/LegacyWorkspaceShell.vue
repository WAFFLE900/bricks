<template>
  <div class="workspace-shell">
    <aside class="workspace-shell__sidebar">
      <slot name="sidebar" />
    </aside>
    <header class="workspace-shell__header">
      <slot name="header" />
    </header>
    <main class="workspace-shell__content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.workspace-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  grid-template-rows: 48px minmax(0, 1fr);
  background: #f2eeee;
}

.workspace-shell__sidebar {
  grid-row: 1 / span 2;
  background: #f2eeee;
}

.workspace-shell__header {
  grid-column: 2;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  z-index: 5;
}

.workspace-shell__content {
  grid-column: 2;
  padding: 2rem 1.5rem;
  background:
    url("@/assets/legacy/bricks_bg_small.svg") top center / cover no-repeat,
    #f2eeee;
  overflow: hidden;
}

@media (max-width: 1100px) {
  .workspace-shell {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto minmax(0, 1fr);
  }

  .workspace-shell__sidebar,
  .workspace-shell__header,
  .workspace-shell__content {
    grid-column: 1;
    grid-row: auto;
  }

  .workspace-shell__content {
    padding: 1rem;
  }
}
</style>
