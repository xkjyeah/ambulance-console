<template>
  <div class="onemap-autocomplete">
    <input type="text" v-model="searchQuery" @input="updateResults"
      :placeholder="placeholder"
      @keydown.prevent.down="selectIndex(selectedIndex + 1)"
      @keydown.prevent.up="selectIndex(selectedIndex - 1)"
      @keydown.prevent.esc="showDropdown = false"
      @keydown.prevent.enter="emitAndDismiss"
      />
    <ul v-if="searchResults && showDropdown" class="onemap-autocomplete-search-results">
      <li v-for="(result, index) in searchResults"
          @click="selectIndex(index), emitAndDismiss(index)"
          :class="{active: result === selectedResult}">
        {{nilOr(result.BLK_NO)}} {{nilOr(result.ROAD_NAME)}}
        {{nilOr(result.BUILDING)}} {{nilOr(result.POSTAL)}}
      </li>
    </ul>
  </div>
</template>

<style lang="scss">
.onemap-autocomplete {
  position: relative;

  input {
  }

  ul.onemap-autocomplete-search-results {
    position: absolute;
    left: 0;
    top: 100%;

    padding: 0;
    margin: 0;
    & > li {
      list-style: none;
      padding: 0.2em;
      margin: 0;
      border: solid 1px #CCC;
      cursor: pointer;
      background-color: white;
      &.active {
        background-color: #DEF;
      }
    }
  }
}
</style>

<script>
import axios from 'axios'
import _ from 'lodash'
import querystring from 'querystring'
import {resultToPlace} from '~/util/onemap'

export default {
  props: ['placeholder', 'text'],
  data () {
    return {
      showDropdown: true,
      searchQuery: '',
      searchResults: [],
      selectedIndex: 0,
      inFlight: false,
      viewingMap: false,
      mapOptions: {
        mapTypeControl: false,
      }
    }
  },
  watch: {
    text: {
      immediate: true,
      handler (t) {
        this.searchQuery = t
      }
    }
  },
  computed: {
    selectedResult () { return this.searchResults[this.selectedIndex] }
  },
  methods: {
    nilOr (s) {
      // Stupid OneMap doesn't use `null`. They use 'NIL'
      return s === 'NIL' ? null : s
    },
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
            const newIndex = response.data.results.findIndex(
              r => r.address === this.searchResults.address
            ) || 0
            this.searchResults = response.data.results
            this.selectedIndex = newIndex
            this.showDropdown = true
            this.inFlight = false
          })
      }
    }, 500, {leading: false, trailing: true}),
    resultToLatLng (r) {
      return {
        lat: parseFloat(r.LATITUDE),
        lng: parseFloat(r.LONGITUDE),
      }
    },
    selectIndex (index) {
      this.selectedIndex =
        Math.min(this.searchResults.length - 1, Math.max(0, index))
    },
    emitAndDismiss () {
      console.log(this.selectedIndex, this.selectedResult)
      if (this.selectedResult) {
        this.searchQuery = this.selectedResult.ADDRESS
        this.$emit('place_changed', resultToPlace(this.selectedResult))
        this.showDropdown = false
      }
    },
    descriptionFromResult (r) {
      return r.ADDRESS
    }
  }
}
</script>
