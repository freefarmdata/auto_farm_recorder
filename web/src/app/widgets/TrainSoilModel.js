// renderTrainModel() {
//   return (
//     <div className="actions__block">
//       <h4>Train A Soil Model</h4>
//       <div className="actions__block--tservice">
//         <input
//           type="datetime-local"
//           onChange={(e) => {
//             this.setState({ modelTrainStart: moment(e.target.value) });
//           }}
//         />
//         <input
//           type="datetime-local"
//           onChange={(e) => {
//             this.setState({ modelTrainEnd: moment(e.target.value) });
//           }}
//         />
//         <button
//           onClick={() => {
//             const { modelTrainStart, modelTrainEnd } = this.state;
//             if (modelTrainStart && modelTrainEnd && modelTrainEnd.isAfter(modelTrainStart)) {
//               this.props.onTrainModel(
//                 modelTrainStart.unix(),
//                 modelTrainEnd.unix()
//               );
//             }
//           }}
//         >
//           Train
//         </button>
//       </div>
//     </div>
//   );
// }