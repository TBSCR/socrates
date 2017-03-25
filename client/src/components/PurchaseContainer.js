import React from 'react';
import PurchaseSelector from './PurchaseSelector'

export default class PurchaseContainer extends React.Component {
  render() {
    return (
      <div className="purchaseContainer">
      	<h1>Get new art every day</h1>
      	<ul>
        	<li><PurchaseSelector label="Name"/></li>
      		<li><PurchaseSelector label="Address"/></li>
      		<li><PurchaseSelector label="Zip"/></li>
      		<li><PurchaseSelector label="City"/></li>
      	</ul>
      </div>
    );
  }
}

