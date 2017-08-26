<template>
  <div class="panel-container">
    <section class="panel vehicle-info">
      <button v-if="!user" @click="login">Login</button>

      <OnemapAutocomplete
        class="main-autocomplete"
        :text="searchString"
        placeholder="Enter address / postal code"
        @place_changed="updateOrigin"
        @input="($event.target.value === '') && updateOrigin(null)"
        />

      <table class="vehicle-results">
        <thead>
          <tr>
            <th>Vehicle</th>
            <th>Location</th>
            <th>Actions</th>
            <th>Dist</th>
            <th>Crew</th>
            <th>Destination</th>
            <th>Busy until</th>
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

          <td class="toolbar-cell" style="white-space: nowrap">
            <button @click="showDispatch(vehicle)">
              »
            </button>
            <Dropdown align="right" style="display: inline-block">
                <div class="menu-button" slot="menu-button">
                  ...
                  <i class="mdi mdi-triangle" />
                </div>
                <template scope="s" slot="dropdown" >
                  <div class="menu-dropdown-buttons">
                    <!-- <button @click="showDispatch(vehicle); s.dismiss()">
                      Dispatch
                    </button> -->
                    <button @click="pushChange(vehicle.registrationno, 'busyUntil', null); s.dismiss()" v-if="!vehicle.status.disabled">
                      Mark as Free
                    </button>
                    <div>
                      <hr/>
                    </div>
                    <button @click="pushChange(vehicle.registrationno, 'disabled', !vehicle.status.disabled);
                                    s.dismiss()">
                      {{ vehicle.status.disabled ? 'Enable' : 'Disable' }}
                    </button>
                </div>
              </template>
            </Dropdown>
          </td>

          <td>
            <template v-if="origin">{{(vehicle.distance / 1000).toFixed(1)}}&nbsp;km</template>
          </td>
          <td>
            <DatasheetCell>
              {{vehicle.status.crew || '\u00a0'}}

              <input type="text" :value="vehicle.status.crew"
                class="the-editor" slot="editor"
                @change="pushChange(vehicle.registrationno, 'crew', $event.target.value)" />
            </DatasheetCell>
          </td>
          <td  class="destination-dropdown-cell">
            <Dropdown align="left" class="destination-dropdown">
              <div class="menu-button" slot="menu-button">
                {{vehicle.status.destinationDescription}}
              </div>
              <div slot="dropdown" class="destination-dropdown-menu"
                  @click="showJob(vehicle, vehicle.status.origin, vehicle.status.destination)">
                <h4>From: {{vehicle.status.originDescription}}</h4>
                <div>{{vehicle.status.originDescriptionExtra}}</div>
                <hr/>
                <h4>To: {{vehicle.status.destinationDescription}}</h4>
                <div>{{vehicle.status.destinationDescriptionExtra}}</div>
                <hr/>
                <h4>{{vehicle.status.details}}</h4>
              </div>
            </Dropdown>
          </td>
          <td>
            <BusyStatus v-if="!vehicle.status.disabled" :value="vehicle.status.busyUntil" />
          </td>
          <!-- <td>
            <DatasheetCell>
              {{vehicle.status.remarks || '\u00a0'}}

              <input type="text" :value="vehicle.status.remarks"
                class="the-editor" slot="editor"
                @change="pushChange(vehicle.registrationno, 'remarks', $event.target.value)" />
            </DatasheetCell>
          </td> -->
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
      <GmapPolyline v-if="selectedJob" :path="[
          selectedJob.origin,
          selectedJob.destination
        ]" :options="dashedLineOptions"
        />
      <GmapPolyline v-if="selectedJob" :path="[
          selectedJob.current,
          selectedJob.destination
        ]" :options="dashedLineOptions"
        />
      <GmapPolyline v-if="selectedJob" :path="[
          selectedJob.origin,
          selectedJob.current,
        ]" :options="dashedLineOptions"
        />
      <GmapMarker v-if="selectedJob"
        label="O"
        :position="selectedJob.origin"
        />
      <GmapMarker v-if="selectedJob"
        label="D"
        :position="selectedJob.destination"
        />
    </GmapMap>

    <!-- <Modal ref="modalHelper" /> -->
    <transition name="swipe-from-right">
      <Dispatch v-if="showDispatching"
        @resolve="submitDispatch"
        @reject="showDispatching = false"
        :originPlace="originPlace"
        :vehicle="dispatchingVehicle"
        class="dispatch-dialog" />
    </transition>
  </div>
</template>

<style lang="scss">
.main-autocomplete input {
  font-size: 110%;
  width: 100%;
}
.dispatch-dialog {
  right: 0;
  width: 40vw;
  top: 4em;
  height: 500px;
  background: white;
  box-shadow: 1px 1px 4px rgba(0,0,0,0.5);
  padding: 1em;
  position: absolute;
}
table.vehicle-results {
  tr {
    &.active td {
      background-color: #def;
    }
    &:hover td {
      background-color: #fed;
    }
    &.disabled td {
      color: #CCC;
      text-decoration: line-through;
    }
  }

  .destination-dropdown {
    & > button {
      background: transparent;
      width: 100%;
      display: block;
      border: none;
      text-align: left;
      padding: 0.5em 0;
      cursor: pointer;
      &:hover {
        background-color: #DCB;
      }
    }
    .destination-dropdown-menu {
      padding: 0.5em;
      background: white;
      box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5);
    }
  }

  .menu-dropdown-buttons {
    display: flex;
    flex-direction: column;
    box-shadow: 0.1em 0.1em 0.2em rgba(0,0,0,0.5);

    button {
      background: transparent;
      border: none;
      padding: 0.5em 0.3em;
      text-align: left;
      min-width: 9em;
      cursor: pointer;

      &:hover {
        background: #FED;
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

<script>
// import {mapState} from 'vuex'
import * as firebase from 'firebase'
import _ from 'lodash'
import OnemapAutocomplete from '~/components/OnemapAutocomplete'
import DatasheetCell from '~/components/DatasheetCell'
import BusyStatus from '~/components/BusyStatus'
import Dispatch from '~/components/Dispatch'
import Dropdown from '~/components/Dropdown'
import Modal from '~/components/Modal'
import iconFromDirection from '~/util/iconFromDirection.js'
import {latlngDistance} from '~/util/geo'

export default {
  components: {
    OnemapAutocomplete, DatasheetCell, BusyStatus, Modal, Dropdown, Dispatch
  },
  data () {
    return {
      searchString: '',
      vehicles: [],
      vehicleStatuses: {},
      selectedVehicle: null,
      dispatchingVehicle: null,
      selectedJob: null,
      user: null,
      origin: null,
      originPlace: null,
      center: {lat: 1.38, lng: 103.8},
      zoom: 11,

      changes: [],
      updatePromise: null,
      showDispatching: false,
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
            details: '',
            destination: null,
            destinationDescription: '',
            destinationDescriptionExtra: '',
            origin: null,
            originDescription: '',
            originDescriptionExtra: '',
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
    },
    dashedLineOptions () {
      return {
        strokeOpacity: 0,
        icons: [{
          icon: {
            path: 'M 0,-1 0,1',
            strokeOpacity: 1,
            scale: 4
          },
          offset: '0',
          repeat: '20px'
        }],
      }
    }
  },
  methods: {
    login () {
      const provider = new firebase.auth.GoogleAuthProvider()
      firebase.auth().signInWithPopup(provider)
    },
    updateOrigin (p) {
      if (p) {
        this.origin = p.location
        this.originPlace = p

        this.center = this.origin
        this.zoom = 15
      } else {
        this.origin = null
      }
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
    },

    showDispatch (vehicle) {
      this.dispatchingVehicle = vehicle
      this.showDispatching = true

      // this.$refs.modalHelper.show(
      //   Dispatch,
      //   {vehicle, originPlace: this.originPlace}
      // )
      //   .then((dispatch) => {
      //     for (let k in dispatch) {
      //       this.pushChange(vehicle.registrationno, k, dispatch[k])
      //     }
      //     this.$refs.modalHelper.hide()
      //   })
      //   .catch(() => {
      //     this.$refs.modalHelper.hide()
      //   })
    },

    submitDispatch ([registrationno, dispatch]) {
      for (let k in dispatch) {
        this.pushChange(registrationno, k, dispatch[k])
      }
      this.showDispatching = false
    },

    showJob (vehicle, origin, destination) {
      if (origin && destination) {
        const current = {
          lat: parseFloat(vehicle.latitude),
          lng: parseFloat(vehicle.longitude),
        }
        console.log(origin, destination, current)
        this.selectedJob = {origin, current, destination}
        this.zoomToPoints(origin, destination)
      }
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
</script>
