import { client, publicSDK } from '@devrev/typescript-sdk';
import axios from 'axios';
import { ApiUtils, HTTPResponse } from './utils';




export const run = async (events: any[]) => {
  for (const event of events) {
    console.log("received query for bot")
    const snapInId = event.context.snap_in_id;  
    const endpoint: string = event.execution_metadata.devrev_endpoint;
    //todo
    const token: string = event.context.secrets.service_account_token;
    const apiUtil: ApiUtils = new ApiUtils(endpoint, token);
    let parameters:string = event.payload.parameters.trim();
    const options = {
        method: 'GET',
        url: `https://devrevhacklimbo.onrender.com/insights?query=${parameters}`,
      };
    console.log("bot : triggereing insights api")
    const insightsApiResponse = await axios.request(options);
    const insightsAPIData = insightsApiResponse.data;  
    console.log("bot : received insights api response")

    let postResp: HTTPResponse = await apiUtil.postTextMessageWithVisibilityTimeout(snapInId, insightsAPIData.response, 5)
    if (!postResp.success) {
      console.error(`Error while creating timeline entry: ${postResp.message}`);
      continue;
    }
  }

}


export default run;