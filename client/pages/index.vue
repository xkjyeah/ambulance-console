<template>
  <div class="panel-container">
    <section class="panel">
      <input type="text" v-model="searchString" />

      <ul>
        <li v-for="vehicle in vehicles">{{vehicle.registrationno}}</li>
      </ul>

    </section>
    <GmapMap :center="{lat: 1.38, lng: 103.8}" :zoom="11" class="panel">
    </GmapMap>
  </div>
</template>

<script>
export default {
  components: {

  }
}
</script>

<style lang="scss">
.panel-container {
  position: fixed;
  top: 0; left: 0; bottom: 0; right: 0;
  display: flex;

  .panel {
    flex: 1 1 50%;
  }
}
</style>
