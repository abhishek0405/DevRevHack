import ticket_creator from './functions/ticket_creator';
import bot_query from './functions/bot_query'
export const functionFactory = {
  // Add your functions here
  ticket_creator,
  bot_query
} as const;

export type FunctionFactoryType = keyof typeof functionFactory;