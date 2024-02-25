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
    sort: gplay.sort.HELPFULNESS,
    num: 200
  });
  const reviews :any= res.data;
  for(const review of reviews){
    console.log("Processing review ",review)
      const date = new Date();
      const ticketName = `Ticket created from Playstore review ${review.id}`;
      const ticketBody = `${review.text}`;
      console.log("calling clustering api for play store review")
      const clusteringServiceOptions = {
        method: 'POST',
        url: 'https://devrevhacklimbo.onrender.com/reviews',
        headers: {
          'content-type': 'application/json',
        },
        data: [
          {
            "review": ticketBody,
            "id": review.id,
            "source": "playstore"
          }
      ]
      };
      const apiResponse = await axios.request(clusteringServiceOptions);
      console.log("received res for playstore review")
      const clusteringData = apiResponse.data;
      if(clusteringData[0].type==="Issue"){
        const response = await devrevSDK.worksCreate({
          title: ticketName,
          body: ticketBody,
          applies_to_part: 'PROD-1',
          owned_by: ['DEVU-1'],
          type: publicSDK.WorkType.Issue,
          tags:[{id:clusteringData[0].tagId}]

        });
        console.log('Issue Ticket created from play store');
      }
      else if(clusteringData.type==="Feature"){
        //figure out if ticket needs to be created
        const response = await devrevSDK.worksCreate({
          title: ticketName,
          body: ticketBody,
          applies_to_part: 'PROD-1',
          owned_by: ['DEVU-1'],
          type: publicSDK.WorkType.Ticket,
          tags:[{id:clusteringData.tagId}]

        });
        console.log('Feature  created from twitter');
      }

    }

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
      hashtag: '#blinkit,#zomato,#letsBLinkIt',
      limit: 20,
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

        if(result.language==="en"){
          const ticketName = `Ticket created from Tweet id ${result.tweet_id}`;
          const ticketBody = `${result.text}`;
          const clusteringServiceOptions = {
            method: 'POST',
            url: 'https://devrevhacklimbo.onrender.com/reviews',
            headers: {
              'content-type': 'application/json',
            },
            data: [
              {
                "review": ticketBody,
                "id": result.tweet_id,
                "source": "twitter"
              }
          ]
          };
          const apiResponse = await axios.request(clusteringServiceOptions);
          const clusteringData = apiResponse.data;
          console.log("received res for tweet from clustering service ",clusteringData)
          if(clusteringData[0].type==="Issue"){
            const response = await devrevSDK.worksCreate({
              title: ticketName,
              body: ticketBody,
              applies_to_part: 'PROD-1',
              owned_by: ['DEVU-1'],
              type: publicSDK.WorkType.Issue,
              tags:[{id:clusteringData[0].tagId}]
  
            });
            console.log('Issue Ticket created from twitter');
          }
          else if(clusteringData.type==="Feature"){
          //figure out if ticket needs to be created
          const response = await devrevSDK.worksCreate({
            title: ticketName,
            body: ticketBody,
            applies_to_part: 'PROD-1',
            owned_by: ['DEVU-1'],
            type: publicSDK.WorkType.Ticket,
            tags:[{id:clusteringData.tagId}]

          });
          console.log('Feature  created from twitter');
        }
        }
      }
    }
   catch (error) {
    console.error(error);
  }
  
}

export const run = async (events: any[]) => {
  for (const event of events) {
    const appId='com.grofers.customerapp'
     await getTweets(event)
     await getPlayStoreReviews(event,appId)
  }

}


export default run;