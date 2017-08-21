<template>
  <div class="panel-container">
    <section class="panel vehicle-info">
      <button v-if="!user" @click="login">Login</button>

      <Geocoder v-model="searchString" @place_changed="updateOrigin"
        @inspect="zoomTo($event)"/>

      <table class="vehicle-results">
        <thead>
          <tr>
            <th>Vehicle</th>
            <th>Location</th>
            <th>Dist</th>
            <th>Crew</th>
            <th>Destination</th>
            <th>Busy until</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
        <tr v-for="vehicle in sortedVehicles" :class="{
          active: selectedVehicle && vehicle.registrationno === selectedVehicle.registrationno,
          disabled: vehicle.status.disabled,
          }">
          <td>
            {{vehicle.registrationno}}
          </td>
          <td>
            <div class="location-preview" :title="vehicle.location"
                @click="selectVehicle(vehicle)">
              {{vehicle.location}}
            </div>
          </td>
          <td>
            <template v-if="origin">{{(vehicle.distance / 1000).toFixed(1)}} km</template>
          </td>
          <td>
            <DatasheetCell>
              {{vehicle.status.crew || '\u00a0'}}

              <input type="text" :value="vehicle.status.crew"
                class="the-editor" slot="editor"
                @change="pushChange(vehicle.registrationno, 'crew', $event.target.value)" />
            </DatasheetCell>
          </td>
          <td>
            {{vehicle.status.destinationDescription}}
          </td>
          <td>
            <BusyStatus v-if="!vehicle.status.disabled" :value="vehicle.status.busyUntil" />
          </td>
          <td class="toolbar-cell">
            <div class="toolbar">
              <button>
                Dispatch
              </button>
              <button>
                End
              </button>
              <button @click="pushChange(vehicle.registrationno, 'disabled', !vehicle.status.disabled)">
                {{ vehicle.status.disabled ? 'Enable' : 'Disable' }}
              </button>
            </div>
          </td>
          <td>
            <DatasheetCell>
              {{vehicle.status.remarks || '\u00a0'}}

              <input type="text" :value="vehicle.status.remarks"
                class="the-editor" slot="editor"
                @change="pushChange(vehicle.registrationno, 'remarks', $event.target.value)" />
            </DatasheetCell>
          </td>
        </tr>
        </tbody>
      </table>

    </section>
    <GmapMap :center="center" :zoom="zoom" class="panel" ref="map">
      <GmapMarker
        label="S"
        :position="origin"
        />
      <GmapMarker :key="vehicle.registrationno" v-for="vehicle in sortedVehicles"
        :position="{
          lat: parseFloat(vehicle.latitude),
          lng: parseFloat(vehicle.longitude)
          }"
        :icon="makeIcon(vehicle.direction, vehicle.registrationno)"
        />
      <GmapPolyline v-if="selectedVehicle && origin"
        :path="[{
          lat: parseFloat(selectedVehicle.latitude),
          lng: parseFloat(selectedVehicle.longitude)
          }, origin]"
        />
    </GmapMap>
  </div>
</template>

<style lang="scss">
table.vehicle-results {
  tr {
    &.active td {
      background-color: #def;
    }
    &:hover td {
      background-color: #fed;
    }
    &.disabled td {
      color: #DDD;
      text-decoration: line-through;
    }
  }

  tr {
    .toolbar-cell:hover {
      overflow: visible;
      z-index: 100;
      .toolbar {
        background-color: #FF0;
        left: -5px;
        top: -5px;
        padding: 5px;
      }
    }
    .toolbar-cell {
      position: relative;
      overflow: hidden;
      z-index: 50;

      .toolbar {
        display: flex;
        flex-direction: column;
        position: absolute;
        left: 0;
        top: 0;
        min-width: 100%;
      }
    }
  }
}

.location-preview {
  max-width: 200px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
  cursor: pointer;
}
</style>

<script>
// import {mapState} from 'vuex'
import * as firebase from 'firebase'
import _ from 'lodash'
import Geocoder from '~/components/Geocoder'
import DatasheetCell from '~/components/DatasheetCell'
import BusyStatus from '~/components/BusyStatus'
import iconFromDirection from '~/util/iconFromDirection.js'

export default {
  components: {
    Geocoder, DatasheetCell, BusyStatus
  },
  data () {
    return {
      searchString: '',
      vehicles: [],
      vehicleStatuses: {},
      selectedVehicle: null,
      user: null,
      origin: null,
      center: {lat: 1.38, lng: 103.8},
      zoom: 11,

      changes: [],
      updatePromise: null,
    }
  },
  mounted () {
    window.onbeforeunload = this.$unload = () => {
      if (this.changes.length > 0) {
        return 'You have unsaved changes. Are you sure you want to navigate away?'
      }
    }

    firebase.database().ref('/locations/ambulance-medical-service')
      .on('value', (v) => {
        this.vehicles = Object.values(v.val())
      })

    firebase.database().ref('/current_status/ambulance-medical-service')
      .on('value', (v) => {
        const val = v.val()
        this.vehicleStatuses = _(val)
          .toPairs()
          .map(([k, v]) => {
            return [k, {
              ...v,
              busyUntil: dateFromString(v.busyUntil)
            }]
          })
          .fromPairs()
          .value()
      })

    this.user = firebase.auth().currentUser
    firebase.auth().onAuthStateChanged(() => {
      this.user = firebase.auth().currentUser
    })
  },
  watch: {
    changes (changes) {
      if (changes.length === 0) {
        return ''
      } else if (this.updatePromise) {
        return ''
      } else {
        const snapshot = _.clone(changes)

        firebase.database().ref('/current_status/ambulance-medical-service')
          .update(
            _(snapshot)
              .map(([veh, key, value]) => [`${veh}/${key.replace(/\./g, '/')}`, value])
              .fromPairs()
              .value()
          )
          .then(() => {
            this.changes = changes.slice(snapshot.length)
          })
      }
    }
  },
  computed: {
    vehiclesWithStatus () {
      return this.vehicles.map(v => {
        const withStatus = {
          ...v,
          status: {
            crew: '',
            remarks: '',
            destination: null,
            destinationDescription: '',
            busyUntil: null,
            ...this.vehicleStatuses[v.registrationno],
          }
        }
        // FIXME inefficient
        for (let c of this.changes) {
          if (c[0] === withStatus.registrationno) {
            _.set(withStatus.status, c[1], c[2])
          }
        }
        return withStatus
      })
    },
    sortedVehicles () {
      if (!this.origin) {
        return _.sortBy(this.vehiclesWithStatus, 'registrationno')
      } else {
        const withDistances = _.map(this.vehiclesWithStatus, vehicle => ({
          ...vehicle,
          distance: latlngDistance(
            [parseFloat(vehicle.latitude), parseFloat(vehicle.longitude)],
            [this.origin.lat, this.origin.lng]
          )
        }))
        return _.sortBy(withDistances, 'distance')
      }
    }
  },
  methods: {
    login () {
      const provider = new firebase.auth.GoogleAuthProvider()
      firebase.auth().signInWithPopup(provider)
    },
    updateOrigin (e) {
      this.origin = e
    },

    zoomTo (ll) {
      if (ll) {
        this.center = ll
        this.zoom = 14
      }
    },
    zoomToPoints (ll1, ll2) {
      if (ll1 && ll2) {
        const bounds = new google.maps.LatLngBounds()
        bounds.extend(ll1)
        bounds.extend(ll2)
        this.$refs.map.fitBounds(bounds)
      } else {
        this.zoomTo(ll1 || ll2)
      }
    },
    selectVehicle (v) {
      this.selectedVehicle = v
      this.zoomToPoints({
        lat: +v.latitude,
        lng: +v.longitude,
      }, this.origin)
    },
    makeIcon (dir, overlay) {
      return iconFromDirection(dir, overlay) || {
        url: 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png',
        anchor: typeof google !== 'undefined' ? new google.maps.Point(35, 35) : null,
      }
    },
    pushChange (vehicle, key, value) {
      this.changes.push([vehicle, key, value])
    }
  }
}

function dateFromString (s) {
  const d = new Date(s)

  if (!isFinite(d.getTime())) {
    return null
  } else {
    return d
  }
}

function latlngDistance (ll1, ll2) {
  var rr1 = [ll1[0] / 180 * Math.PI, ll1[1] / 180 * Math.PI]
  var rr2 = [ll2[0] / 180 * Math.PI, ll2[1] / 180 * Math.PI]

  var dx = (rr1[1] - rr2[1]) * Math.cos(0.5 * (rr1[0] + rr2[0]))
  var dy = rr1[0] - rr2[0]

  var dist = Math.sqrt(dx * dx + dy * dy) * 6371000
  return dist
}
</script>

<style lang="scss">
.panel-container {
  position: fixed;
  top: 0; left: 0; bottom: 0; right: 0;
  display: flex;

  .panel {
    flex: 1 1 50%;

    &.vehicle-info {
      overflow: scroll;
    }
  }
}
</style>
