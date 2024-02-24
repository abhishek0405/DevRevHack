import { client, publicSDK } from '@devrev/typescript-sdk';
import gplay from "google-play-scraper";
import axios from 'axios';
import { createClient } from 'redis';

// const redisClient:any  = createClient({
//   password: 'x8rWrY7WuyyQHhPnDAEm4ZajTQvPNE9',
//   socket: {
//       host: 'redis-15229.c281.us-east-1-2.ec2.cloud.redislabs.com',
//       port: 15229
//   }
// })

// // Handle Redis errors
// redisClient.on('error', (err:any) => {
//   console.error('Redis Error:', err);
// });



const getPlayStoreReviews = async(event:any,appId:any)=>{
  try{
  const endpoint = event.execution_metadata.devrev_endpoint;
  const token = event.context.secrets.service_account_token;

  // Initialize the public SDK client
  const devrevSDK = client.setup({ endpoint, token });
  const res:any = await gplay.reviews({
    appId: appId,
    sort: gplay.sort.NEWEST,
    num: 10
  });
  const reviews :any= res.data;
  for(const review of reviews){
    console.log(`Processsing review id ${review.id}`)
    // const reviewProcessed = await redisClient.get(review.id);
    // if(reviewProcessed!==true){
      // await redisClient.set(review.id,true);
      const date = new Date();
      const ticketName = `Ticket created from Playstore review ${review.id}`;
      const ticketBody = `${review.text}`;
      const response = await devrevSDK.worksCreate({
        title: ticketName,
        body: ticketBody,
        // The ticket will be created in the PROD-1 part. Rename this to match your part.
        applies_to_part: 'PROD-1',
        // The ticket will be owned by the DEVU-1 team. Rename this to match the required user.
        owned_by: ['DEVU-1'],
        type: publicSDK.WorkType.Ticket,
        // tags:[{id:"play_store_tag"}]
      });
      console.log('Ticket created from playstore');
    }
  //   else{
  //     console.log(`Already processed ${review.id}`)
  //   }
  // }
}
catch(e){
  console.log(e);
}
}

const getTweets = async(event:any)=>{
  const options = {
    method: 'POST',
    url: 'https://twitter154.p.rapidapi.com/hashtag/hashtag',
    headers: {
      'content-type': 'application/json',
      'X-RapidAPI-Key': '0412993968msh8256fea080f2a3bp1fa130jsn278ae6e2b3f8',
      'X-RapidAPI-Host': 'twitter154.p.rapidapi.com'
    },
    data: {
      hashtag: '#blinkit',
      limit: 5,
      section: 'top',
      language: 'en'
    }
  };
  
  try {
    const endpoint = event.execution_metadata.devrev_endpoint;
    const token = event.context.secrets.service_account_token;
  
    // Initialize the public SDK client
    const devrevSDK = client.setup({ endpoint, token });
    const response = await axios.request(options);
    const results = response.data.results;
    for(const result of results){
      console.log("Processing tweet id "+ result.tweet_id)
      //check if exists
      // const tweetProcessed = await redisClient.get(result.tweet_id);
      // if(tweetProcessed!==true){
        // await redisClient.set(result.tweet_id,true);
        if(result.language==="en"){
          const ticketName = `Ticket created from Tweet id ${result.tweet_id}`;
          const ticketBody = `${result.text}`;
          //figure out if ticket needs to be created
          const response = await devrevSDK.worksCreate({
            title: ticketName,
            body: ticketBody,
            // The ticket will be created in the PROD-1 part. Rename this to match your part.
            applies_to_part: 'PROD-1',
            // The ticket will be owned by the DEVU-1 team. Rename this to match the required user.
            owned_by: ['DEVU-1'],
            type: publicSDK.WorkType.Ticket,
            tags:[{id:"twitter_tag",value:"twitter"}]

          });
          console.log('Ticket created from twitter');
        }
      }
      // else{
      //   console.log(`Already processed ${result.tweet_id}`)
      // }
      // }
    }
   catch (error) {
    console.error(error);
  }
  
}

export const run = async (events: any[]) => {
  for (const event of events) {
    // if(redisClient===null){
    //    redisClient = createClient({
    //     password: 'x8rWrY7WuyyQHhPnDAEm4ZajTQvPNE9',
    //     socket: {
    //         host: 'redis-15229.c281.us-east-1-2.ec2.cloud.redislabs.com',
    //         port: 15229
    //     }
    // })
    const appId='com.grofers.customerapp'
    // getTweets(event)
    await getPlayStoreReviews(event,appId)
  }

}


export default run;