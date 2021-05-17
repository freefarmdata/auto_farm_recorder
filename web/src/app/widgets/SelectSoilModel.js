// renderSelectModel() {
//   const { info } = this.props;

//   if (!info || !info.soil_models.length) {
//     return;
//   }

//   return (
//     <div className="actions__block">
//     <h4>Select A Soil Model</h4>
//     <div className="actions__block--sservice">
//         <table>
//           <thead>
//             <tr>
//               <th>Name</th>
//               <th>Start</th>
//               <th>End</th>
//               <th>Error</th>
//               <th>Activate</th>
//               <th>Delete</th>
//             </tr>
//           </thead>
//           <tbody>
//             {info.soil_models.map((model, i) => {
//               return (
//                 <tr key={i} className={model.active.toString()}>
//                   <td>{model.name}</td>
//                   <td>{moment(model.start_time*1E3).format('dddd, MMM Do YYYY, h:mm:ss a')}</td>
//                   <td>{moment(model.end_time*1E3).format('dddd, MMM Do YYYY, h:mm:ss a')}</td>
//                   <td>{model.error.toFixed(5)}</td>
//                   <td>
//                     <button
//                       onClick={() => {
//                         this.props.selectModel(model.name);
//                       }}
//                     >
//                       Select
//                     </button>
//                   </td>
//                   <td>
//                     <button
//                       onClick={() => {
//                         this.props.deleteModel(model.name);
//                       }}
//                     >
//                       Delete
//                     </button>
//                   </td>
//                 </tr>
//               )
//             })}
//           </tbody>
//         </table>
//       </div>
//     </div>
//   );
// }