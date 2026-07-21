const C={
  paper:'#f1efe9',white:'#fffefa',ink:'#15212b',muted:'#66727e',line:'#d8d5cd',
  sim:'#4477aa',weight:'#ee8b2d',truth:'#745fc2',valid:'#238f83',alert:'#c94f52'
};

const sequences=[
  {
    key:'scaling', label:'Why matrices stop scaling', short:'Scaling', steps:5,
    builds:[
      ['Start from familiar territory: one truth axis, one reconstructed axis.','Establishes that the argument is about representation, not a rejection of D’Agostini unfolding.'],
      ['Now add a second observable on both the truth and reconstructed sides.','Makes the often-hidden square-of-the-state-space scaling explicit.'],
      ['Add a third coordinate without adding events.','Shows why sparse response matrices arrive much sooner than intuition based only on truth-bin counts.'],
      ['Name the actual tradeoff: physics resolution versus matrix occupancy.','Turns “curse of dimensionality” jargon into the analysis choice collaborators recognize.'],
      ['Change representation: keep one row per simulated event and add columns.','Creates the opening for event-level likelihood ratios without claiming that the statistical problem disappears.']
    ]
  },
  {
    key:'bridge', label:'Before the matrix was histogrammed', short:'D’Agostini bridge', steps:5,
    builds:[
      ['Follow one simulated interaction from truth to its reconstructed partner.','Begins with the concrete object both methods share: a paired simulated event.'],
      ['The simulation is an ensemble of these pairs, including migration.','Makes detector response visible before introducing bins or machine learning.'],
      ['Histogram those pairs and you obtain the response matrix.','Demystifies the matrix as a compressed representation of the same paired ensemble.'],
      ['D’Agostini assigns a correction to truth bins.','Anchors the weighting interpretation in a method the collaboration already knows.'],
      ['OmniFold keeps the pairs and learns weights at event resolution.','Positions OmniFold as a change in representation and ratio estimation—not an unrelated black box.']
    ]
  },
  {
    key:'ratio', label:'The classifier is a ratio meter', short:'Ratio meter', steps:4,
    builds:[
      ['Show data and simulation occupying the same reconstructed feature space.','Prevents the classifier from being introduced as an abstract ML object.'],
      ['Ask only where data are more or less dense than simulation.','Reframes classification as a local density-comparison task.'],
      ['Convert the classifier probability into a likelihood-ratio weight.','Provides the one equation worth retaining and explains what the output means physically.'],
      ['Apply the weights: simulation density morphs toward data density.','Closes the loop visually before the audience sees the two-level OmniFold algorithm.']
    ]
  },
  {
    key:'algorithm', label:'One complete OmniFold iteration', short:'OmniFold iteration', steps:6,
    builds:[
      ['Inventory the inputs: measured reco events and paired truth/reco simulation, including misses.','Makes clear which information is—and is not—available in data.'],
      ['Push the current truth weights through the simulated pairs to reconstructed space.','Introduces “push” as bookkeeping through a known simulated event identity.'],
      ['Step 1: compare weighted reconstructed simulation with data.','Shows exactly where the data constrain the weights.'],
      ['Pull the learned detector-space correction back through each pair.','Shows the crucial reco-to-truth information path and the native miss treatment.'],
      ['Step 2: learn a smooth truth-space reweight that becomes the next push.','Corrects the common oversimplification that OmniFold merely copies weights once.'],
      ['Iterate until changes are small; retain the weighted truth ensemble.','Ends on the actual product and identifies iteration/model capacity as regularization.']
    ]
  },
  {
    key:'output', label:'What “bin at the end” buys', short:'Bin at the end', steps:4,
    builds:[
      ['The result is a weighted truth-level event record, not one histogram.','Makes the output object tangible before claiming flexibility.'],
      ['Choose the published two-dimensional binning for the trust check.','Connects the event-level product to a conventional cross-section result.'],
      ['Project the same weighted record onto a different stored truth coordinate.','Shows reuse without implying that arbitrary hidden observables are automatically unbiased.'],
      ['Change bin edges or inspect several projections without rerunning the unfold.','States the practical payoff in a form directly relevant to analysis iteration and publication.']
    ]
  },
  {
    key:'marginal', label:'Marginalization is the validation', short:'Marginalization', steps:4,
    builds:[
      ['Begin with a simultaneous three-coordinate result.','Frames added dimensions as an obligation to preserve established information.'],
      ['Sum over the new coordinate cell by cell.','Makes marginalization a concrete linear operation rather than a vague projection.'],
      ['Compare the marginal with the established lower-dimensional anchor.','Elevates the agreement requirement to a gate, not an attractive afterthought.'],
      ['End on the cleared MINERvA marginal-anchor result.','Moves from the toy explanation to evidence that the production chain passes the check.']
    ]
  }
];

let active=0, step=0, timer=null;
const slide=typeof document!=='undefined'?document.querySelector('#slide'):null;

const E=(tag,a='',b='')=>`<${tag} ${a}>${b}</${tag}>`;
const xml=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;');
const tx=(x,y,s,size=24,fill=C.ink,weight=500,anchor='start',extra='')=>E('text',`x="${x}" y="${y}" font-size="${size}" fill="${fill}" font-weight="${weight}" text-anchor="${anchor}" ${extra}`,xml(s));
const rect=(x,y,w,h,fill='none',stroke=C.line,rx=0,sw=1,op=1)=>E('rect',`x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}" fill-opacity="${op}" stroke="${stroke}" stroke-width="${sw}"`);
const line=(x1,y1,x2,y2,stroke=C.line,sw=2,dash='',marker='')=>E('line',`x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${stroke}" stroke-width="${sw}" ${dash?`stroke-dasharray="${dash}"`:''} ${marker?`marker-end="url(#${marker})"`:''}`);
const circle=(x,y,r,fill,op=1,stroke='none',sw=0)=>E('circle',`cx="${x}" cy="${y}" r="${r}" fill="${fill}" fill-opacity="${op}" stroke="${stroke}" stroke-width="${sw}"`);
const path=(d,stroke=C.line,sw=2,fill='none',op=1,dash='',marker='')=>E('path',`d="${d}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" opacity="${op}" ${dash?`stroke-dasharray="${dash}"`:''} ${marker?`marker-end="url(#${marker})"`:''}`);
const pill=(x,y,w,label,fill,ink=C.white)=>rect(x,y,w,34,fill,'none',17,0)+tx(x+w/2,y+23,label,14,ink,750,'middle');
const arrowDefs=()=>`<defs>
  <marker id="arrowSim" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0 0L9 4.5 0 9Z" fill="${C.sim}"/></marker>
  <marker id="arrowWeight" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0 0L9 4.5 0 9Z" fill="${C.weight}"/></marker>
  <marker id="arrowTruth" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0 0L9 4.5 0 9Z" fill="${C.truth}"/></marker>
  <marker id="arrowValid" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0 0L9 4.5 0 9Z" fill="${C.valid}"/></marker>
</defs>`;

function chrome(title,kicker,takeaway,tag='CONCEPTUAL TOY'){
  return arrowDefs()+tx(70,58,kicker.toUpperCase(),13,C.truth,800)+tx(70,105,title,39,C.ink,730)+
    pill(1234,43,136,tag,C.paper,C.muted)+
    rect(62,728,1316,54,C.paper,'none',12,0)+circle(91,755,6,C.weight)+tx(112,763,takeaway,22,C.ink,680);
}

function matrix(x,y,n,size,mode='dense',labels=true){
  let o=''; const cell=size/n;
  for(let j=0;j<n;j++) for(let i=0;i<n;i++){
    const diag=Math.exp(-Math.pow(i-j,2)/(2*Math.max(1,n/8)));
    let op=mode==='dense'?.08+.78*diag:(((i*17+j*11)%37===0)?.62:.018+.08*diag);
    o+=rect(x+i*cell,y+j*cell,cell,cell,C.sim,C.white,0,.5,op);
  }
  o+=rect(x,y,size,size,'none',C.ink,1,2);
  if(labels){
    o+=tx(x+size/2,y+size+34,'reconstructed state',15,C.muted,650,'middle');
    o+=tx(x-34,y+size/2,'truth state',15,C.muted,650,'middle',`transform="rotate(-90 ${x-34} ${y+size/2})"`);
  }
  return o;
}

function numberCard(x,y,label,state,cells,color=C.sim){
  return rect(x,y,350,110,C.white,C.line,12,1)+tx(x+22,y+29,label,13,C.muted,750)+
    tx(x+22,y+59,state,18,C.ink,700)+tx(x+22,y+91,`${cells} response cells`,22,color,760);
}

function scaling(s){
  let take=['A response matrix scales with truth states × reconstructed states.','Two observables make the state space square—and the response matrix squares it again.','The matrix grows; the event sample does not.','Fine physics resolution and stable matrix inversion pull in opposite directions.','Event-level methods keep the pairs and add features as columns.'][s];
  let o=chrome('Why response matrices stop scaling','Start from D’Agostini IBU',take);
  if(s<=2){
    const dims=s+1, n=[7,14,24][s], mode=s===2?'sparse':'dense';
    o+=tx(84,158,`${dims} observable${dims>1?'s':''}`,20,C.muted,700);
    o+=matrix(125,195,n,420,mode);
    const exponent=2*dims;
    o+=tx(760,180,'Illustration: 10 bins per axis',18,C.muted,650);
    if(s>=0) o+=numberCard(760,210,'ONE OBSERVABLE','10 truth × 10 reco','100');
    if(s>=1) o+=numberCard(760,338,'TWO OBSERVABLES','100 truth × 100 reco','10,000',C.weight);
    if(s>=2) o+=numberCard(760,466,'THREE OBSERVABLES','1,000 truth × 1,000 reco','1,000,000',C.alert);
    o+=tx(1180,637,`response cells scale as b^${exponent}`,28,s===2?C.alert:C.sim,760,'end');
    o+=tx(1180,666,'b = bins per observable',14,C.muted,600,'end');
  } else if(s===3){
    o+=rect(115,190,500,430,C.white,C.line,16,1)+rect(825,190,500,430,C.white,C.line,16,1);
    o+=tx(365,238,'Physics asks for',22,C.muted,650,'middle')+tx(365,282,'finer bins',38,C.truth,760,'middle');
    for(let n=0;n<4;n++){
      const w=310+n*28, gap=w/(5+n*2);
      for(let i=0;i<=5+n*2;i++) o+=line(365-w/2+i*gap,335,365-w/2+i*gap,515,C.truth,.8);
      o+=line(365-w/2,335+n*34,365+w/2,335+n*34,C.truth,.8);
    }
    o+=tx(1075,238,'Stable inversion asks for',22,C.muted,650,'middle')+tx(1075,282,'populated cells',38,C.sim,760,'middle');
    o+=matrix(915,330,8,315,'dense',false);
    o+=path('M645 405 C720 360 750 360 795 405 M645 455 C720 500 750 500 795 455',C.alert,4,'none',1,'','arrowWeight');
    o+=tx(720,445,'tradeoff',20,C.alert,760,'middle');
  } else {
    o+=tx(83,161,'Response-matrix representation',17,C.muted,720)+tx(790,161,'Event-level representation',17,C.muted,720);
    o+=matrix(110,205,16,390,'sparse');
    o+=tx(305,653,'new observable → many new cells',17,C.alert,700,'middle');
    o+=rect(740,195,575,390,C.white,C.line,14,1);
    const cols=[['event','70'],['truth pT','178'],['reco pT','278'],['truth p∥','378'],['reco p∥','478']];
    cols.forEach((c,i)=>o+=tx(770+Number(c[1]),235,c[0],13,C.muted,750,'middle'));
    for(let r=0;r<7;r++){
      o+=line(758,258+r*40,1295,258+r*40,C.line,1);
      o+=circle(784,278+r*40,5,C.sim,.7);
      for(let c=1;c<5;c++) o+=rect(835+(c-1)*100,269+r*40,62,16,C.sim,'none',3,0,.12+(r+c)%4*.1);
    }
    o+=rect(1150,208,142,350,C.weight,C.weight,10,2,.08);
    o+=tx(1221,610,'+ 2 columns',22,C.weight,760,'middle')+tx(1221,638,'per observable',15,C.muted,650,'middle');
  }
  return o;
}

const pairSet=Array.from({length:16},(_,i)=>{
  const txv=150+i*65, tyv=235+48*Math.sin(i*.79)+((i%3)-1)*13;
  const rxv=txv+38*Math.sin(i*1.46), ryv=515+55*Math.sin(i*.79+.85)+((i%4)-1.5)*9;
  return {tx:txv,ty:tyv,rx:rxv,ry:ryv,w:.65+((i*7)%8)*.16};
});

function zones(){
  return tx(92,169,'TRUTH',13,C.truth,800)+tx(92,426,'RECONSTRUCTED',13,C.sim,800)+
    line(80,380,1360,380,C.line,2)+tx(1335,368,'detector',13,C.muted,650,'end');
}

function drawPairs(color=C.sim,weighted=false,showLines=true){
  let o=''; pairSet.forEach((p,i)=>{
    if(showLines)o+=line(p.tx,p.ty,p.rx,p.ry,C.line,1);
    o+=circle(p.tx,p.ty,weighted?5+3*p.w:6,color,weighted?.78:.58)+circle(p.rx,p.ry,weighted?5+3*p.w:6,color,weighted?.78:.78);
  }); return o;
}

function bridge(s){
  let takes=['Every simulated interaction already comes as a truth–reco pair.','Detector response is the ensemble of how those pairs migrate.','A response matrix is that paired ensemble after histogramming.','D’Agostini estimates how much each truth bin should count.','OmniFold estimates how much each simulated event should count.'];
  let o=chrome('The response matrix, before it was histogrammed','The conceptual bridge',takes[s])+zones();
  if(s===0){
    const p=pairSet[7];
    o+=circle(p.tx,p.ty,13,C.truth,.9)+circle(p.rx,p.ry,13,C.sim,.9)+line(p.tx,p.ty,p.rx,p.ry,C.ink,3,'7 7');
    o+=tx(p.tx+30,p.ty-12,'true event record',20,C.truth,700)+tx(p.rx+30,p.ry+8,'reconstructed partner',20,C.sim,700);
    o+=pill(560,322,320,'same simulated event ID',C.ink);
  } else if(s===1){
    o+=drawPairs();
    o+=tx(1130,242,'migration',18,C.muted,700)+path('M1115 255 C1065 285 1075 420 1115 475',C.sim,3,'none',1,'7 7','arrowSim');
  } else if(s===2){
    o+=tx(340,155,'paired simulated events',18,C.muted,700,'middle')+drawPairs(C.sim,false,true);
    o+=path('M690 635 C790 670 815 670 880 635',C.weight,4,'none',1,'','arrowWeight');
    o+=matrix(940,195,10,350,'dense');
    o+=tx(1115,585,'count pairs in each cell',18,C.sim,720,'middle');
    o+=rect(660,180,3,430,C.line,'none',0,0);
  } else if(s===3){
    o+=matrix(110,195,9,410,'dense');
    const weights=[.65,.8,1.15,1.45,1.1,.9,.72,.6,.55];
    weights.forEach((w,j)=>{
      o+=rect(110,195+j*45.55,410,45.55,w>1?C.weight:C.sim,'none',0,0,.08+Math.abs(w-1)*.18);
      o+=tx(555,224+j*45.55,`w${j+1} = ${w.toFixed(2)}`,15,w>1?C.weight:C.sim,700);
    });
    o+=tx(900,270,'one correction',32,C.ink,740,'middle')+tx(900,313,'per truth bin',32,C.truth,740,'middle');
    o+=tx(900,385,'All events in that bin',18,C.muted,600,'middle')+tx(900,414,'share the same update.',18,C.muted,600,'middle');
  } else {
    o+=drawPairs(C.weight,true,true);
    pairSet.forEach((p,i)=>{ if(i%3===0)o+=tx(p.tx,p.ty-15,`×${p.w.toFixed(1)}`,12,C.weight,750,'middle'); });
    o+=rect(1010,190,300,425,C.paper,'none',14,0);
    o+=tx(1160,242,'Keep event resolution',25,C.ink,740,'middle');
    o+=circle(1058,286,4,C.valid)+tx(1075,292,'paired truth and reco',18,C.muted,650)+circle(1058,329,4,C.valid)+tx(1075,335,'several observables',18,C.muted,650)+circle(1058,372,4,C.valid)+tx(1075,378,'continuous features',18,C.muted,650);
    o+=tx(1160,475,'learn one weight',27,C.weight,760,'middle')+tx(1160,510,'per event',27,C.weight,760,'middle');
  }
  return o;
}

const simPts=Array.from({length:45},(_,i)=>({
  x:180+((i*79)%680), y:205+((i*47+(i%4)*17)%390), cluster:i%3,
  w:i%3===0?1.75:(i%3===1?.58:1.02)
}));
const dataPts=Array.from({length:43},(_,i)=>({
  x:195+((i*83+(i%3)*55)%665), y:210+((i*53+(i%5)*23)%385)
}));

function axes(x=120,y=640,w=820,h=470){
  return line(x,y,x+w,y,C.ink,2)+line(x,y,x,y-h,C.ink,2)+tx(x+w/2,y+42,'reconstructed feature 1',16,C.muted,650,'middle')+
    tx(x-48,y-h/2,'feature 2',16,C.muted,650,'middle',`transform="rotate(-90 ${x-48} ${y-h/2})"`);
}

function ratio(s){
  let takes=['The classifier sees ordinary reconstructed observables.','It answers a local question: where is data denser than simulation?','With balanced training samples, classifier probability becomes a density ratio.','The ratio becomes an event weight; the weighted simulation follows the data density.'];
  let o=chrome('A classifier is a local density-ratio meter','Remove the ML mystery',takes[s]);
  if(s<3){
    o+=axes();
    simPts.forEach(p=>o+=circle(p.x,p.y,5,C.sim,.58));
    dataPts.forEach(p=>o+=circle(p.x,p.y,3.5,C.ink,.86));
    if(s>=1){
      o+=rect(185,190,270,205,C.weight,C.weight,22,3,.06)+rect(590,400,260,195,C.sim,C.sim,22,3,.05);
      o+=tx(320,225,'data denser',20,C.weight,760,'middle')+tx(720,435,'simulation denser',20,C.sim,760,'middle');
      o+=tx(320,372,'weight > 1',17,C.weight,700,'middle')+tx(720,572,'weight < 1',17,C.sim,700,'middle');
    }
    o+=rect(1000,190,330,390,C.paper,'none',16,0);
    if(s===0){
      o+=tx(1165,260,'Input',16,C.muted,750,'middle')+circle(1090,310,6,C.ink)+tx(1110,317,'measured data',18,C.ink,650)+circle(1090,356,7,C.sim,.75)+tx(1110,363,'reco simulation',18,C.ink,650);
      o+=tx(1165,452,'No truth labels',20,C.ink,720,'middle')+tx(1165,482,'are used here.',20,C.ink,720,'middle');
    } else if(s===1){
      o+=tx(1165,245,'The useful output is not',17,C.muted,650,'middle')+tx(1165,292,'“data or MC?”',28,C.ink,760,'middle')+tx(1165,362,'It is the local',17,C.muted,650,'middle')+tx(1165,405,'data / simulation',27,C.weight,760,'middle')+tx(1165,442,'density ratio.',27,C.weight,760,'middle');
    } else {
      o+=tx(1165,250,'classifier output',17,C.muted,700,'middle')+tx(1165,300,'p(data | x)',31,C.truth,760,'middle')+line(1050,333,1280,333,C.line,2)+tx(1165,385,'event weight',17,C.muted,700,'middle')+tx(1165,438,'w(x) =  p',29,C.weight,760,'middle')+tx(1197,460,'1 − p',18,C.weight,760,'middle')+line(1180,442,1244,442,C.weight,2)+tx(1165,515,'balanced training priors',12,C.muted,600,'middle');
    }
  } else {
    o+=axes();
    dataPts.forEach(p=>o+=circle(p.x,p.y,3.3,C.ink,.72));
    simPts.forEach(p=>o+=circle(p.x,p.y,4+3*p.w,C.weight,.28+.32*Math.min(1,p.w)));
    o+=rect(990,190,340,390,C.paper,'none',16,0)+tx(1160,242,'After reweighting',18,C.muted,700,'middle');
    o+=circle(1070,305,5,C.ink,.9)+tx(1090,312,'data density',18,C.ink,650)+circle(1070,350,9,C.weight,.7)+tx(1090,357,'weighted simulation',18,C.ink,650);
    o+=tx(1160,435,'The points did not move.',19,C.ink,700,'middle')+tx(1160,470,'Only how much each',19,C.ink,700,'middle')+tx(1160,505,'event counts changed.',19,C.weight,760,'middle');
  }
  return o;
}

const algoPairs=Array.from({length:12},(_,i)=>{
  const txv=180+i*75, tyv=225+40*Math.sin(i*.91), rxv=txv+35*Math.sin(i*1.51), ryv=505+45*Math.sin(i*.91+.8);
  return {tx:txv,ty:tyv,rx:rxv,ry:ryv,w:.65+(i%5)*.23,miss:i===10};
});
const algoData=Array.from({length:15},(_,i)=>({x:165+i*58+22*Math.sin(i*1.3),y:515+38*Math.sin(i*.74+.2)}));

function algoBase(){
  let o=zones();
  algoPairs.forEach(p=>{
    if(!p.miss)o+=line(p.tx,p.ty,p.rx,p.ry,C.line,1);
    else o+=line(p.tx,p.ty,p.tx,p.ty+115,C.line,1,'5 6');
  });
  algoData.forEach(p=>o+=circle(p.x,p.y,4,C.ink,.88));
  return o;
}

function algorithm(s){
  let takes=['Data exist only at reconstructed level; simulation supplies the truth–reco pairing.','Current truth weights ride with each simulated event into detector space.','The detector-space classifier learns the correction required by the data.','The correction returns to truth through event identity; misses receive a truth-feature estimate.','A second classifier expresses the pulled correction as a smooth truth-space weight for the next iteration.','After a controlled number of iterations, the weighted truth ensemble is the unfolded result.'];
  let o=chrome('One complete OmniFold iteration','The two-step algorithm',takes[s])+algoBase();
  if(s===0){
    algoPairs.forEach(p=>o+=circle(p.tx,p.ty,6,p.miss?C.truth:C.sim,.62,p.miss?C.truth:'none',p.miss?2:0)+(p.miss?'':circle(p.rx,p.ry,6,C.sim,.7)));
    o+=pill(1025,195,260,'SIMULATION: paired',C.sim)+pill(1025,468,260,'DATA: reco only',C.ink);
    o+=tx(1105,305,'truth-only miss',15,C.truth,700)+line(1090,312,930,275,C.truth,2,'','arrowTruth');
  } else if(s===1){
    algoPairs.forEach(p=>{
      o+=circle(p.tx,p.ty,5+2*p.w,C.truth,.72);
      if(!p.miss)o+=circle(p.rx,p.ry,5+2*p.w,C.sim,.72);
      o+=tx(p.tx,p.ty-15,`q=${p.w.toFixed(1)}`,11,C.truth,700,'middle');
    });
    o+=path('M1050 270 C1130 315 1130 420 1050 470',C.sim,4,'none',1,'','arrowSim');
    o+=tx(1170,350,'PUSH',22,C.sim,800,'middle')+tx(1170,380,'same event weights',14,C.muted,650,'middle');
  } else if(s===2){
    algoPairs.forEach(p=>{o+=circle(p.tx,p.ty,6,C.truth,.32);if(!p.miss)o+=circle(p.rx,p.ry,5+3*p.w,C.weight,.82);});
    o+=rect(1010,430,320,175,C.paper,'none',14,0)+tx(1170,466,'STEP 1 · DETECTOR SPACE',13,C.weight,800,'middle')+tx(1170,510,'data',22,C.ink,720,'middle')+tx(1170,545,'vs',15,C.muted,650,'middle')+tx(1170,579,'pushed simulation',22,C.sim,720,'middle');
    o+=tx(665,650,'learn rdet(xreco)',22,C.weight,760,'middle');
  } else if(s===3){
    algoPairs.forEach((p,i)=>{
      if(!p.miss){
        o+=circle(p.rx,p.ry,5+2*p.w,C.weight,.42);
        const q=.48, x=p.rx+(p.tx-p.rx)*q, y=p.ry+(p.ty-p.ry)*q;
        o+=circle(x,y,5+2*p.w,C.weight,.95,C.white,1)+circle(p.tx,p.ty,5+2*p.w,C.weight,.62);
      } else o+=circle(p.tx,p.ty,8,C.truth,.25,C.truth,2);
    });
    o+=path('M1110 470 C1185 410 1185 320 1110 260',C.weight,4,'none',1,'','arrowWeight')+tx(1200,360,'PULL',22,C.weight,800,'middle');
    o+=rect(980,188,350,112,C.paper,'none',12,0)+tx(1155,220,'truth-only misses',14,C.truth,760,'middle')+tx(1155,251,'estimate rdet from truth neighbors',16,C.ink,650,'middle')+tx(1155,278,'(native acceptance treatment)',12,C.muted,600,'middle');
  } else if(s===4){
    algoPairs.forEach(p=>o+=circle(p.tx,p.ty,5+3*p.w,C.weight,.76)+(p.miss?'':circle(p.rx,p.ry,5,C.sim,.18)));
    o+=rect(965,175,390,178,C.paper,'none',14,0)+tx(1160,212,'STEP 2 · TRUTH SPACE',13,C.truth,800,'middle')+tx(1160,252,'original truth',20,C.sim,700,'middle')+tx(1160,280,'vs pulled-weight truth',20,C.weight,700,'middle')+tx(1160,321,'learn smooth qnext(xtruth)',18,C.truth,760,'middle');
    o+=path('M1160 365 C1260 410 1260 520 1120 552',C.truth,4,'none',1,'7 7','arrowTruth')+tx(1215,454,'next push',17,C.truth,750,'middle');
  } else {
    algoPairs.forEach(p=>o+=circle(p.tx,p.ty,5+3*p.w,C.weight,.88)+(p.miss?'':circle(p.rx,p.ry,4+2*p.w,C.weight,.28)));
    o+=path('M1030 250 C1270 250 1270 525 1030 525',C.truth,4,'none',1,'8 9')+tx(1230,388,'repeat',22,C.truth,800,'middle');
    o+=rect(945,185,390,150,C.paper,'none',14,0)+tx(1140,226,'REGULARIZATION',13,C.muted,800,'middle')+tx(1140,267,'iterations + learner capacity',19,C.ink,720,'middle')+tx(1140,302,'validated by closure and stability',15,C.valid,680,'middle');
    o+=pill(975,560,330,'WEIGHTED TRUTH ENSEMBLE',C.weight);
  }
  return o;
}

const rows=Array.from({length:8},(_,i)=>({w:(.7+(i%5)*.22).toFixed(2),pt:(.08+i*.11).toFixed(2),pz:(2.0+i*.62).toFixed(1),ea:(.05+(i%4)*.16).toFixed(2),q3:(.25+(i%6)*.17).toFixed(2),W:(.9+(i%5)*.28).toFixed(2)}));

function eventTable(x,y,w,h){
  const headers=['event weight','pT truth','p∥ truth','Eavail truth','q3 truth','W truth'];
  let o=rect(x,y,w,h,C.white,C.line,12,1); const cw=w/headers.length;
  headers.forEach((h0,i)=>o+=tx(x+cw*(i+.5),y+34,h0,13,i===0?C.weight:C.muted,760,'middle'));
  rows.forEach((r,j)=>{
    const vals=[r.w,r.pt,r.pz,r.ea,r.q3,r.W];
    o+=line(x+14,y+53+j*38,x+w-14,y+53+j*38,C.line,.8);
    vals.forEach((v,i)=>o+=tx(x+cw*(i+.5),y+78+j*38,v,14,i===0?C.weight:C.ink,i===0?760:570,'middle'));
  });
  return o;
}

function heatmap(x,y,w,h,color=C.weight){
  let o=rect(x,y,w,h,C.paper,C.ink,2,1.5);
  for(let i=0;i<8;i++)for(let j=0;j<6;j++){
    const v=.08+(((i*5+j*7)%13)/13)*.72;
    o+=rect(x+i*w/8,y+j*h/6,w/8,h/6,color,C.white,0,.5,v);
  }
  return o;
}
function hist(x,y,w,h,color=C.weight,n=9){
  const vals=Array.from({length:n},(_,i)=>2+((i*7+3)%11)+7*Math.exp(-Math.pow(i-n*.48,2)/(n*.9)));
  let o=line(x,y+h,x+w,y+h,C.ink,1.5)+line(x,y+h,x,y,C.ink,1.5); const max=Math.max(...vals),bw=w/n;
  vals.forEach((v,i)=>o+=rect(x+4+i*bw,y+h-v/max*(h-10),bw-7,v/max*(h-10),color,'none',3,0,.72)); return o;
}

function output(s){
  let takes=['The unfolded object retains a weight and a truth record for each simulated event.','For the reproduction, histogram those events in the published (pT,p∥) bins.','The same weighted events can be projected onto another stored truth coordinate.','Alternative binnings and several projections come from the same unfolded ensemble.'];
  let o=chrome('The result is not one histogram','What “bin at the end” buys',takes[s]);
  if(s===0){
    o+=eventTable(130,175,1180,385)+pill(510,610,420,'UNFOLDED EVENT-LEVEL PRODUCT',C.weight);
  } else if(s===1){
    o+=eventTable(85,178,650,390)+path('M765 365 C830 365 835 365 875 365',C.weight,4,'none',1,'','arrowWeight');
    o+=heatmap(925,205,350,320,C.weight)+tx(1100,565,'published (pT, p∥) binning',18,C.ink,700,'middle')+pill(995,604,210,'TRUST CHECK',C.valid);
  } else if(s===2){
    o+=eventTable(85,178,650,390)+path('M765 365 C830 365 835 365 875 365',C.truth,4,'none',1,'','arrowTruth');
    o+=hist(920,235,375,280,C.truth,10)+tx(1107,558,'projection onto Eavail',18,C.ink,700,'middle')+tx(1107,590,'from the same event weights',14,C.muted,650,'middle');
  } else {
    o+=rect(95,175,390,410,C.paper,'none',16,0)+tx(290,215,'weighted truth events',17,C.weight,760,'middle');
    rows.forEach((r,i)=>o+=circle(155+(i*89)%270,265+(i*53)%260,6+Number(r.w)*3,C.weight,.68));
    o+=path('M510 375 C570 375 590 245 635 245',C.weight,3,'none',1,'','arrowWeight')+path('M510 375 C570 375 590 390 635 390',C.valid,3,'none',1,'','arrowValid')+path('M510 375 C570 375 590 535 635 535',C.truth,3,'none',1,'','arrowTruth');
    o+=rect(660,158,650,170,C.white,C.line,12,1)+heatmap(695,185,190,115,C.weight)+tx(1065,235,'published 2D bins',18,C.ink,700,'middle');
    o+=rect(660,343,650,135,C.white,C.line,12,1)+hist(700,370,270,75,C.valid,7)+tx(1110,415,'coarser / finer binning',18,C.ink,700,'middle');
    o+=rect(660,493,650,135,C.white,C.line,12,1)+hist(700,520,270,75,C.truth,10)+tx(1110,565,'another stored projection',18,C.ink,700,'middle');
  }
  return o;
}

function cube(x,y,w,h,depth){
  let o=path(`M${x} ${y+depth} L${x+w} ${y+depth} L${x+w} ${y+h+depth} L${x} ${y+h+depth} Z`,C.ink,1.6)+
    path(`M${x} ${y+depth} L${x+depth} ${y} L${x+w+depth} ${y} L${x+w} ${y+depth} M${x+w} ${y+h+depth} L${x+w+depth} ${y+h} L${x+w+depth} ${y}`,C.line,1.6);
  for(let k=0;k<5;k++){
    const xx=x+k*w/5; o+=line(xx,y+depth,xx,y+h+depth,C.line,.7);
  }
  for(let j=0;j<4;j++){
    const yy=y+depth+j*h/4;o+=line(x,yy,x+w,yy,C.line,.7);
  }
  for(let d=0;d<4;d++){
    const off=d*depth/4;
    o+=rect(x+off,y+depth-off,w,h,C.weight,'none',0,0,.025+d*.022);
  }
  return o;
}

function marginal(s){
  let takes=['A 3D result contains one (pT,p∥) plane for every Eavail interval.','Summing those planes over Eavail produces a 2D marginal.','That marginal must agree with the established 2D measurement within the validated comparison.','The production higher-dimensional result passes this anchor at central-value level.'];
  let o=chrome('Every new dimension must return to the anchor','Marginalization as validation',takes[s],s===3?'REAL RESULT':'CONCEPTUAL TOY');
  if(s===0){
    o+=cube(260,205,610,330,150)+tx(565,620,'(pT, p∥, Eavail)',24,C.weight,760,'middle');
    o+=tx(1080,265,'one 2D plane',20,C.muted,700,'middle')+tx(1080,300,'per Eavail slice',30,C.truth,760,'middle');
    for(let k=0;k<5;k++)o+=rect(1010+k*13,360-k*10,190,135,C.weight,C.white,2,.8,.05+k*.08);
  } else if(s===1){
    for(let k=0;k<5;k++){
      o+=rect(150+k*22,205-k*15,350,260,C.weight,C.white,2,1,.05+k*.07);
      o+=tx(105+k*22,350-k*15,`E${k+1}`,14,C.muted,700,'middle');
    }
    o+=path('M620 330 C720 330 730 330 800 330',C.weight,5,'none',1,'','arrowWeight')+tx(710,305,'Σ over Eavail',19,C.weight,760,'middle');
    o+=heatmap(880,190,390,360,C.weight)+tx(1075,595,'2D marginal in (pT, p∥)',21,C.ink,720,'middle');
  } else if(s===2){
    o+=tx(360,170,'3D → 2D marginal',18,C.weight,750,'middle')+heatmap(155,205,410,350,C.weight);
    o+=tx(1080,170,'established 2D anchor',18,C.valid,750,'middle')+heatmap(875,205,410,350,C.valid);
    o+=path('M610 380 C690 380 735 380 815 380',C.valid,4,'none',1,'','arrowValid');
    o+=pill(595,595,250,'COMPARE CELL BY CELL',C.valid);
    o+=tx(720,660,'Normalization · shape · pulls',18,C.muted,680,'middle');
  } else {
    o+=rect(110,140,1220,545,C.white,C.line,12,1);
    o+=E('image',`href="../../claude-design-package/figures/eavail_marginal_vs_paper_pull_full.png" x="145" y="160" width="1150" height="495" preserveAspectRatio="xMidYMid meet"`);
    o+=pill(1030,160,225,'CLEARED CENTRAL VALUE',C.valid);
  }
  return o;
}

const renderers={scaling,bridge,ratio,algorithm,output,marginal};

function render(){
  const seq=sequences[active], build=seq.builds[step];
  slide.innerHTML=E('g','class="enter"',renderers[seq.key](step));
  document.querySelector('#kicker').textContent=`Sequence ${active+1} · build ${step+1}`;
  document.querySelector('#sequenceTitle').textContent=seq.label;
  document.querySelector('#speaker').textContent=build[0];
  document.querySelector('#intent').textContent=build[1];
  document.querySelector('#counter').textContent=`${step+1} / ${seq.steps}`;
  document.querySelector('#play').textContent=timer?'Pause':'Play';
  document.querySelectorAll('#tabs button').forEach((b,i)=>b.classList.toggle('active',i===active));
}
function stop(){ if(timer){clearInterval(timer);timer=null;} }
function advance(delta=1){ const seq=sequences[active]; step=(step+delta+seq.steps)%seq.steps; render(); }
function setSequence(i){ stop(); active=i; step=0; render(); }
function play(){ if(timer){stop();render();return;} timer=setInterval(()=>advance(1),2400);render(); }

if(typeof module!=='undefined') module.exports={sequences,renderers,C};

if(typeof document!=='undefined'){
  const tabs=document.querySelector('#tabs');
  sequences.forEach((seq,i)=>{const b=document.createElement('button');b.textContent=`${i+1} · ${seq.short}`;b.onclick=()=>setSequence(i);tabs.appendChild(b);});
  document.querySelector('#prev').onclick=()=>{stop();advance(-1)};
  document.querySelector('#next').onclick=()=>{stop();advance(1)};
  document.querySelector('#play').onclick=play;
  document.addEventListener('keydown',e=>{
    if(e.key==='ArrowLeft'){stop();advance(-1)}
    if(e.key==='ArrowRight'){stop();advance(1)}
    if(e.key===' '){e.preventDefault();play()}
    if('123456'.includes(e.key))setSequence(Number(e.key)-1);
  });
  render();
}
