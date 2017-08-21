<template>
  <div>
    <div>
      <input type="text" v-model="searchQuery" @input="updateResults"
        placeholder="Search here!"
        />
    </div>
    <ul v-if="searchResults" class="geocoder-search-results">
      <li v-for="result in searchResults.slice(0,3)"
          @click="selectResult(result)"
          :class="{active: result === selectedResult}">
        {{result.BLK_NO}} {{result.ROAD_NAME}} {{result.BUILDING}} {{result.POSTAL}}

        <button @click="$emit('inspect', resultToLatLng(result))">
          inspect
        </button>
      </li>
    </ul>
  </div>
</template>

<style lang="scss">
ul.geocoder-search-results {
  padding: 0;
  margin: 0;
  & > li {
    list-style: none;
    padding: 0.2em;
    margin: 0;
    border: solid 1px #CCC;
    cursor: pointer;
    &.active {
      background-color: #DEF;
    }
  }
}
</style>

<script>
import axios from 'axios'
import _ from 'lodash'
import querystring from 'querystring'

export default {
  name: 'app',
  data () {
    return {
      searchQuery: '',
      searchResults: [],
      selectedResult: null,
      inFlight: false,
      viewingMap: false,
      mapOptions: {
        mapTypeControl: false,
      }
    }
  },
  methods: {
    updateResults: _.throttle(function () {
      if (this.searchQuery === '') {
        this.searchResults = ''
      } else {
        this.inFlight = true
        axios.get(`https://developers.onemap.sg/commonapi/search?` + querystring.stringify({
          searchVal: this.searchQuery,
          returnGeom: 'Y',
          getAddrDetails: 'Y'
        }))
          .then((response) => {
            this.searchResults = response.data.results
            this.selectedResult = (this.searchResults && this.searchResults.length > 0)
              ? this.searchResults[0]
              : null
            this.inFlight = false

            if (this.selectedResult) {
              this.selectResult(this.selectedResult)
            }
          })
      }
    }, 500, {leading: false, trailing: true}),
    resultToLatLng (r) {
      return {
        lat: parseFloat(r.LATITUDE),
        lng: parseFloat(r.LONGITUDE),
      }
    },
    selectResult (r) {
      this.selectedResult = r
      this.$emit('place_changed', this.resultToLatLng(r))
    }
  }
}
</script>
